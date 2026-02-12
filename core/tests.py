from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Category, Module, Course, Chapter, Lesson, Enrollment


User = get_user_model()


class ElearningModelTest(TestCase):

    def setUp(self):
        # Users
        self.teacher = User.objects.create_user(
            username="teacher1",
            password="testpass123",
            role="teacher"
        )

        self.student = User.objects.create_user(
            username="student1",
            password="testpass123",
            role="student"
        )

        # Category
        self.category = Category.objects.create(name="Programmation")

        # Module
        self.module = Module.objects.create(
            name="Python",
            category=self.category
        )

        # Course
        self.course = Course.objects.create(
            module=self.module,
            teacher=self.teacher,
            title="Python Débutant",
            description="Cours pour apprendre Python"
        )

        # Chapter
        self.chapter = Chapter.objects.create(
            course=self.course,
            name="Bases",
            description="Introduction aux bases",
            order=1
        )

        # Lesson
        self.lesson = Lesson.objects.create(
            chapter=self.chapter,
            title="Variables",
            content="Les variables permettent de stocker des données.",
            order=1
        )

    # ==========================
    # TESTS
    # ==========================

    def test_category_created(self):
        self.assertEqual(self.category.name, "Programmation")

    def test_module_relation(self):
        self.assertEqual(self.module.category, self.category)

    def test_course_teacher(self):
        self.assertEqual(self.course.teacher, self.teacher)

    def test_chapter_belongs_to_course(self):
        self.assertEqual(self.chapter.course, self.course)

    def test_lesson_belongs_to_chapter(self):
        self.assertEqual(self.lesson.chapter, self.chapter)

    def test_enrollment_creation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)

    def test_only_student_can_enroll(self):
        enrollment = Enrollment(
            student=self.teacher,
            course=self.course
        )

        with self.assertRaises(ValidationError):
            enrollment.clean()

    def test_unique_enrollment(self):
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        with self.assertRaises(Exception):
            Enrollment.objects.create(
                student=self.student,
                course=self.course
            )
