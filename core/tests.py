from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from core.models import (
    Category, Module, Course,
    Chapter, Lesson, LessonVideo,
    Enrollment
)

User = get_user_model()


class ModelTestBase(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher1",
            password="pass123",
            role=User.TEACHER
        )

        self.student = User.objects.create_user(
            username="student1",
            password="pass123",
            role=User.STUDENT
        )

        self.category = Category.objects.create(name="Développement")

        self.module = Module.objects.create(
            name="Python",
            category=self.category
        )

        self.course = Course.objects.create(
            module=self.module,
            teacher=self.teacher,
            title="Django Masterclass",
            description="Apprendre Django"
        )

        self.chapter = Chapter.objects.create(
            course=self.course,
            name="Introduction",
            description="Chapitre 1",
            order=1
        )

        self.lesson = Lesson.objects.create(
            chapter=self.chapter,
            title="Premiers pas",
            content="Contenu...",
            order=1
        )


# ==============================
# USER TESTS
# ==============================

class UserModelTest(ModelTestBase):

    def test_user_role_properties(self):
        self.assertTrue(self.teacher.is_teacher)
        self.assertFalse(self.teacher.is_student)

        self.assertTrue(self.student.is_student)
        self.assertFalse(self.student.is_teacher)


# ==============================
# CATEGORY & MODULE
# ==============================

class CategoryModuleTest(ModelTestBase):

    def test_category_str(self):
        self.assertEqual(str(self.category), "Développement")

    def test_module_unique_per_category(self):
        with self.assertRaises(IntegrityError):
            Module.objects.create(
                name="Python",
                category=self.category
            )


# ==============================
# COURSE
# ==============================

class CourseModelTest(ModelTestBase):

    def test_course_str(self):
        self.assertEqual(str(self.course), "Django Masterclass")

    def test_unique_course_title_per_teacher(self):
        with self.assertRaises(IntegrityError):
            Course.objects.create(
                module=self.module,
                teacher=self.teacher,
                title="Django Masterclass",
                description="Duplicate"
            )

    '''def test_get_absolute_url(self):
        url = self.course.get_absolute_url()
        expected = reverse('course_detail', kwargs={'slug': self.course.slug})
        self.assertEqual(url, expected)'''


# ==============================
# CHAPTER
# ==============================

class ChapterModelTest(ModelTestBase):

    def test_chapter_str(self):
        self.assertEqual(
            str(self.chapter),
            "Chapitre 1 - Introduction"
        )

    def test_unique_chapter_order_per_course(self):
        with self.assertRaises(IntegrityError):
            Chapter.objects.create(
                course=self.course,
                name="Autre",
                description="Test",
                order=1
            )


# ==============================
# LESSON
# ==============================

class LessonModelTest(ModelTestBase):

    def test_lesson_str(self):
        self.assertEqual(
            str(self.lesson),
            "Leçon 1 - Premiers pas"
        )

    def test_unique_lesson_order(self):
        with self.assertRaises(IntegrityError):
            Lesson.objects.create(
                chapter=self.chapter,
                title="Autre leçon",
                content="Test",
                order=1
            )

    '''def test_get_absolute_url(self):
        url = self.lesson.get_absolute_url()

        expected = reverse(
            'lesson_detail',
            kwargs={
                'category_slug': self.category.slug,
                'course_slug': self.course.slug,
                'chapter_slug': self.chapter.slug,
                'lesson_slug': self.lesson.slug,
            }
        )

        self.assertEqual(url, expected)'''


# ==============================
# LESSON VIDEO
# ==============================

class LessonVideoTest(ModelTestBase):

    def test_video_creation(self):
        video = SimpleUploadedFile(
            "video.mp4",
            b"file_content",
            content_type="video/mp4"
        )

        lesson_video = LessonVideo.objects.create(
            lesson=self.lesson,
            video_file=video,
            order=1
        )

        self.assertEqual(str(lesson_video), f"Vidéo 1 - {self.lesson.title}")

    def test_unique_video_order(self):
        video1 = SimpleUploadedFile("video1.mp4", b"x", content_type="video/mp4")
        LessonVideo.objects.create(
            lesson=self.lesson,
            video_file=video1,
            order=1
        )

        video2 = SimpleUploadedFile("video2.mp4", b"x", content_type="video/mp4")

        with self.assertRaises(IntegrityError):
            LessonVideo.objects.create(
                lesson=self.lesson,
                video_file=video2,
                order=1
            )


# ==============================
# ENROLLMENT
# ==============================

class EnrollmentTest(ModelTestBase):

    def test_student_can_enroll(self):
        enrollment = Enrollment(
            student=self.student,
            course=self.course
        )
        enrollment.full_clean()
        enrollment.save()

        self.assertEqual(
            str(enrollment),
            f"{self.student.username} inscrit à {self.course.title}"
        )

    def test_teacher_cannot_enroll(self):
        enrollment = Enrollment(
            student=self.teacher,
            course=self.course
        )

        with self.assertRaises(ValidationError):
            enrollment.full_clean()

    def test_unique_enrollment(self):
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                course=self.course
            )
