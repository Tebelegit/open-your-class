from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import (
    Category,
    Course,
    Chapter,
    Lesson,
    Enrollment
)

User = get_user_model()


class CourseSchemaTestCase(TestCase):

    def setUp(self):
        # ---------- User ----------
        self.teacher = User.objects.create_user(
            username="teacher1",
            password="password123",
            role=User.TEACHER
        )

        self.student = User.objects.create_user(
            username="student1",
            password="password123",
            role=User.STUDENT
        )

        # ---------- Category ----------
        self.category = Category.objects.create(
            name="Programmation"
        )

        # ---------- Course ----------
        self.course = Course.objects.create(
            category=self.category,
            teacher=self.teacher,
            name="Apprendre Python de zéro",
            description="Cours pour débutants en Python",
            is_published=True
        )

        # ---------- Chapter ----------
        self.chapter = Chapter.objects.create(
            course=self.course,
            name="Comprendre le fonctionnement de Python",
            description="Introduction générale au langage Python",
            order=1
        )

        # ---------- Lesson ----------
        self.lesson = Lesson.objects.create(
            chapter=self.chapter,
            title="Les variables",
            content="Une variable permet de stocker une valeur",
            order=1
        )

        # ---------- Enrollment ----------
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    # =========================
    # BASIC MODEL TESTS
    # =========================

    def test_category_str(self):
        self.assertEqual(str(self.category), "Programmation")

    def test_course_str(self):
        self.assertEqual(str(self.course), "Apprendre Python de zéro")

    def test_chapter_str(self):
        self.assertEqual(
            str(self.chapter),
            "Chapitre 1 : Comprendre le fonctionnement de Python"
        )

    def test_lesson_str(self):
        self.assertEqual(
            str(self.lesson),
            "Leçon 1 : Les variables"
        )

    # =========================
    # RELATIONSHIP TESTS
    # =========================

    def test_course_has_chapters(self):
        self.assertEqual(self.course.chapters.count(), 1)

    def test_chapter_has_lessons(self):
        self.assertEqual(self.chapter.lessons.count(), 1)

    def test_student_enrolled_in_course(self):
        self.assertEqual(self.student.enrollments.count(), 1)
        self.assertEqual(self.course.enrollments.count(), 1)

    # =========================
    # URL TESTS
    # =========================

    '''def test_course_absolute_url(self):
        url = self.course.get_absolute_url()
        self.assertEqual(url, reverse('course_detail', kwargs={'slug': self.course.slug}))

    def test_chapter_absolute_url(self):
        url = self.chapter.get_absolute_url()
        self.assertEqual(url, reverse('chapter_detail', kwargs={'slug': self.chapter.slug}))

    def test_lesson_absolute_url(self):
        url = self.lesson.get_absolute_url()
        self.assertEqual(
            url,
            reverse(
                'lesson_detail',
                kwargs={
                    'chapter_slug': self.chapter.slug,
                    'lesson_slug': self.lesson.slug
                }
            )
        )'''

    # =========================
    # BUSINESS LOGIC TESTS
    # =========================

    def test_teacher_role(self):
        self.assertTrue(self.teacher.is_teacher)
        self.assertFalse(self.teacher.is_student)

    def test_student_role(self):
        self.assertTrue(self.student.is_student)
        self.assertFalse(self.student.is_teacher)
