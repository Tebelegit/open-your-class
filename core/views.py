from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    TemplateView, ListView, DetailView
)
from .models import (
    Category, Module, Course, Chapter, Lesson, Enrollment
)

# Create your views here.

class IndexView(TemplateView):
    template_name = 'index.html'

class CategoryListView(ListView):
    model = Category
    template_name = 'core/list/category_list.html'
    context_object_name = 'categories'
   # paginate_by = 3

    def get_queryset(self):
        return Category.objects.all().prefetch_related('modules')

class ModuleListView(ListView):
    model = Module
    template_name = 'core/list/module_list.html'

class CourseListView(ListView):
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

class ChapterListView(ListView):
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