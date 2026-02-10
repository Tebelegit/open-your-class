from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    TemplateView, ListView, DetailView
)
from .models import (
    Category, Course, Chapter, Lesson, Enrollment
)

# Create your views here.

class IndexView(TemplateView):
    template_name = 'index.html'


class CategoryListView(ListView):
    model = Category
    template_name = 'core/list/category_list.html'
    context_object_name = 'categories'
   # paginate_by = 3


class ChapterListView(ListView):
    model = Chapter
    template_name = 'core/list/chapter_list.html'
    context_object_name = 'chapters'

    def get_queryset(self):
        course = Course.objects.get(
            name__iexact=self.kwargs['course_name'],
            category__slug=self.kwargs['category_slug'],
            is_published=True
        )

        return Chapter.objects.filter(course=course).order_by('order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = Course.objects.get(
            name__iexact=self.kwargs['course_name'],
            category__slug=self.kwargs['category_slug'],
            is_published=True
        )

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
                'chapter',
                'chapter__course',
                'chapter__course__category'
            )
            .filter(
                slug=self.kwargs['lesson_slug'],
                chapter__order=self.kwargs['chapter_order'],
                chapter__course__name=self.kwargs['course_name'],
                chapter__course__category__slug=self.kwargs['category_slug'],
            )
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_lesson = self.object
        chapter = current_lesson.chapter
        course = chapter.course 

        context['all_lessons'] = Lesson.objects.filter(chapter=chapter).order_by('order')

        context['previous_lesson'] = Lesson.objects.filter(
            chapter=chapter,
            order__lt=current_lesson.order
        ).order_by('-order').first()

        next_lesson = Lesson.objects.filter(
            chapter=chapter,
            order__gt=current_lesson.order
        ).order_by('order').first()
        context['next_lesson'] = next_lesson

        if not next_lesson:
            next_chapter = Chapter.objects.filter(
                course=course,
                order__gt=chapter.order
            ).order_by('order').first()

            if next_chapter:
                context['next_chapter_lesson'] = Lesson.objects.filter(
                    chapter=next_chapter
                ).order_by('order').first()
            else:
                context['next_chapter_lesson'] = None
        else:
            context['next_chapter_lesson'] = None

        return context

