from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    TheUser, Category, Course, Chapter, Lesson, Enrollment
)

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('order', 'title', 'content', 'slug')

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ('order', 'name', 'slug')

class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    fields = ('name', 'teacher', 'is_published')

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1
    raw_id_fields = ('student',)

@admin.register(TheUser)
class TheUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    list_editable = ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('Rôle & Permissions', {'fields': ('role',)}),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    inlines = [CourseInline]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'teacher', 'is_published', 'created_at')
    list_filter = ('category', 'is_published', 'teacher')
    search_fields = ('name', 'description')
    inlines = [ChapterInline, EnrollmentInline]

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('name',)
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter', 'order')
    list_filter = ('chapter__course', 'chapter')
    search_fields = ('title', 'content')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'created_at')
    list_filter = ('course', 'created_at')
    raw_id_fields = ('student',)