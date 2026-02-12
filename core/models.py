from django.urls import reverse
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
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
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name

class Module(SlugBaseModel, BaseTimeStamp):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="modules"
    )
    name = models.CharField(max_length=200)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name'],
                name='unique_module_per_category'
            )
        ]
        ordering = ['name']

    def __str__(self):
        return self.name

class Course(SlugBaseModel, BaseTimeStamp):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='courses',
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_taught'
    )

    title = models.CharField(max_length=150)
    description = models.TextField()
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'title'],
                name='unique_course_title_per_teacher'
            )
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})

class Chapter(SlugBaseModel, BaseTimeStamp):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='chapters'
    )

    name = models.CharField(max_length=150)
    description = models.TextField()
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'name'],
                name='unique_chapter_name_per_course'
            ),
            models.UniqueConstraint(
                fields=['course', 'order'],
                name='unique_chapter_order_per_course'
            )
        ]

    def __str__(self):
        return f"Chapitre {self.order} - {self.name}"

class Lesson(SlugBaseModel, BaseTimeStamp):
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='lessons'
    )

    title = models.CharField(max_length=150)
    content = models.TextField()

    video_file = models.FileField(
        upload_to='lessons/videos/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['mp4', 'mkv'],
                message="Formats autorisés : .mp4, .mkv"
            )
        ],
        max_length=1000
    )

    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(
                fields=['chapter', 'title'],
                name='unique_lesson_title_per_chapter'
            ),
            models.UniqueConstraint(
                fields=['chapter', 'order'],
                name='unique_lesson_order_per_chapter'
            )
        ]

    def __str__(self):
        return f"Leçon {self.order} - {self.title}"

    def get_absolute_url(self):
        return reverse(
            'lesson_detail',
            kwargs={
                'category_slug': self.chapter.course.module.category.slug,
                'module_slug': self.chapter.course.module.slug,
                'course_slug': self.chapter.course.slug,
                'chapter_slug': self.chapter.slug,
                'lesson_slug': self.slug,
            }
        )

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

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'],
                name='unique_student_course_enrollment'
            )
        ]

    def clean(self):
        if not self.student.is_student:
            raise ValidationError("Seuls les étudiants peuvent s'inscrire à un cours.")

    def __str__(self):
        return f"{self.student.username} inscrit à {self.course.title}"
