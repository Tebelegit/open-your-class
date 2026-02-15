from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import (
    TheUser, Category, Module, Course, Chapter, Lesson, Enrollment
)

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import (
    CourseCreateForm, RegisterForm, LoginForm
)
# Create your views here.

class IndexView(TemplateView):
    template_name = 'index.html'

class CategoryListView(ListView):
    model = Category
    template_name = 'core/list/category_list.html'
    context_object_name = 'categories'
    login_url = 'login'
    paginate_by = 3

    def get_queryset(self):
        return Category.objects.all().prefetch_related('modules')

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'core/list/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        self.module = get_object_or_404(
            Module, 
            slug=self.kwargs['module_slug'],
            category__slug=self.kwargs['category_slug']
        )
        return Course.objects.filter(module=self.module, is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['module'] = self.module 
        return context

class ChapterListView(LoginRequiredMixin, ListView):
    model = Chapter
    template_name = 'core/list/chapter_list.html'
    context_object_name = 'chapters'

    def get_queryset(self):
        self.course = get_object_or_404(
            Course,
            slug=self.kwargs['course_slug'],
            module__slug=self.kwargs['module_slug'],
            module__category__slug=self.kwargs['category_slug']
        )

        return Chapter.objects.filter(course=self.course).prefetch_related(
            'lessons__chapter__course__module__category'
        ).order_by('order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course

        user = self.request.user
        if user.is_authenticated and user.is_student:
            Enrollment.objects.get_or_create(
                student=user,
                course=self.course
            )
        else:
            raise PermissionDenied

        return context
    
class LessonDetailView(DetailView):
    model = Lesson
    template_name = 'core/detail/current_lesson_detail.html'
    context_object_name = 'current_lesson'
    slug_url_kwarg = 'lesson_slug'

    def get_queryset(self):
        return (
            Lesson.objects
            .select_related(
                'chapter__course__module__category'
            )
            .filter(
                slug=self.kwargs['lesson_slug'],
                chapter__slug=self.kwargs['chapter_slug'],
                # Correction de la chaîne ici : course -> module -> slug
                chapter__course__module__slug=self.kwargs['module_slug'],
                chapter__course__slug=self.kwargs['course_slug'],
                # Correction de la chaîne ici : course -> module -> category -> slug
                chapter__course__module__category__slug=self.kwargs['category_slug'],
            )
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_lesson = self.object
        chapter = current_lesson.chapter
        course = chapter.course 

        # OPTIMISATION ICI : On ajoute select_related pour le sommaire
        context['all_lessons'] = Lesson.objects.filter(chapter=chapter).select_related(
            'chapter__course__module__category'
        ).order_by('order')

        # Navigation (C'est déjà assez léger ici)
        context['previous_lesson'] = Lesson.objects.filter(
            chapter=chapter, order__lt=current_lesson.order
        ).order_by('-order').first()

        next_lesson = Lesson.objects.filter(
            chapter=chapter, order__gt=current_lesson.order
        ).order_by('order').first()
        context['next_lesson'] = next_lesson

        if not next_lesson:
            next_chapter = Chapter.objects.filter(
                course=course, order__gt=chapter.order
            ).order_by('order').first()

            if next_chapter:
                # OPTIMISATION ICI : select_related pour le lien du chapitre suivant
                context['next_chapter_lesson'] = Lesson.objects.filter(
                    chapter=next_chapter
                ).select_related('chapter__course__module__category').order_by('order').first()
                
        return context

''' cours suivi/vu par un student ou enrollment '''
@login_required
def course_tracking(request, category_slug, module_slug, course_slug):
    if not request.user.is_student:
        raise PermissionDenied

    course = get_object_or_404(Course, slug=course_slug)
    Enrollment.objects.create(student=request.user, course=course)

    return redirect(
        'chapter_list',
        category_slug=category_slug,
        module_sug=module_slug,
        course_slug=course_slug  
    )

''' forms '''
class RegisterView(CreateView):
    model = TheUser
    form_class = RegisterForm
    template_name = 'core/auth/register.html'
  #  success_url = 'login'

    def form_valid(self, form):
        user = form.save()
        
        if user.role == 'teacher':
            group = Group.objects.get('teacher-group')
        else:
            group = Group.objects.get('student-group')

        user.groups.add(group)

        login(self.request, user)
        messages.success(self.request, 'inscription reussie.')
        return super().form_valid(form)

    
    def form_invalid(self, form):
        return super().form_invalid(form)
    
class CustomLoginFormView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm
    
class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseCreateForm
    template_name = 'core/create/create_course.html'
    success_url = reverse_lazy('index')

    # seul un teacher cree des cours.
    def test_func(self):
        return self.request.user.teacher

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

    
''' profile '''
@login_required
def dashboard_view(request):
    if request.user.is_teacher:
        return redirect('dashboard_teacher')
    
    elif request.user.is_student:
        return redirect('dashboard_student')
    
    else:
        return redirect('index')
    

@login_required
def dashboard_teacher_view(request):
    if not request.user.is_teacher:
        raise PermissionDenied
    
    courses_taught = request.user.courses_taught.filter(
        is_published=True
    ).select_related('module__category')
    paginator = Paginator(courses_taught, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'courses': courses_taught,
        'page_obj': page_obj
    }
    return render(request, 'core/profile/teacher_profile.html', context)

@login_required
def dashboard_student_view(request):
    if not request.user.is_student:
        raise PermissionDenied

    booked_courses = request.user.enrollments.select_related('course__module__category')
    context = {
        'booked_courses': booked_courses
    }

    return render(request, 'core/profile/student_profile.html', context)

''' 404 '''
def custom_404(request, exception):

    popular_courses = Course.objects.filter(
        is_published=True
    ).select_related(
        "module__category", "teacher"
    )[:3]

    categories = Category.objects.all()[:5]

    context = {
        "popular_courses": popular_courses,
        "categories": categories,
    }

    return render(request, "404.html", context, status=404)

