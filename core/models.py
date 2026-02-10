from django.urls import reverse
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from .utils import BaseTimeStamp, SlugBaseModel


class TheUser(AbstractUser):
    STUDENT = 'student'
    TEACHER = 'teacher'

    ROLE_CHOICES = (
        (STUDENT, 'Apprenant'),
        (TEACHER, 'Enseignant'),
    )

    role = models.CharField(
        choices=ROLE_CHOICES,
        default=STUDENT,
        max_length=10
    )

    @property
    def is_teacher(self):
        return self.role == self.TEACHER

    @property
    def is_student(self):
        return self.role == self.STUDENT


class Category(SlugBaseModel, BaseTimeStamp):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Catégorie de cours'
        verbose_name_plural = 'Catégories de cours'


class Course(SlugBaseModel, BaseTimeStamp):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught'
    )
    name = models.CharField(max_length=150)
    description = models.TextField()
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Course'
        ordering = ['-created_at']


class Chapter(SlugBaseModel, BaseTimeStamp):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='chapters'
    )
    name = models.CharField(max_length=150)
    description = models.TextField(
        help_text="présentation globale du chapitre (objectifs, contexte)"
    )
    video_file = models.FileField(
        max_length=1000,
        upload_to='chapters/videos/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp4', 'mkv'],
                message="erreur. formats autorisés : .mp4, .mkv"
            )
        ]
    )
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Chapitre {self.order} : {self.name}'

    def get_absolute_url(self):
        return reverse('chapter_detail', kwargs={'chapter_slug': self.slug})

    class Meta:
        verbose_name = 'Chapitre'
        ordering = ['order']


class Lesson(SlugBaseModel, BaseTimeStamp):
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=150)
    content = models.TextField(
        help_text="content ciblé : un concept précis"
    )
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Leçon {self.order} : {self.title}'

    def get_absolute_url(self):
        return reverse(
            'lesson_detail',
            kwargs={
                'category_slug': self.chapter.course.category.slug,
                'course_name': self.chapter.course.name,
                'chapter_order': self.chapter.order,
                'lesson_slug': self.slug,
            }
        )

    class Meta:
        verbose_name = 'Leçon'
        ordering = ['order']


class Enrollment(BaseTimeStamp):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    def __str__(self):
        return f'{self.student.username} s\'est inscris sur le cours : {self.course} '

    class Meta:
        verbose_name = 'Inscription au course'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'],
                name='unique_student_course_enrollment'
            )
        ]
