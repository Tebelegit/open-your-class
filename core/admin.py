from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    TheUser, Category, Module, Course, Chapter, Lesson, Enrollment
)

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    exclude = ('slug',)
    fields = ('order', 'title', 'content')

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    exclude = ('slug',)
    fields = ('order', 'name')

class CourseInline(admin.TabularInline):
    model = Course
    extra = 1
    exclude = ('slug',)
    fields = ('title', 'teacher', 'is_published')

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    exclude = ('slug',)
    fields = ('name',)

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
    list_display = ('name',)
    exclude = ('slug',)
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    exclude = ('slug',)
    inlines = [CourseInline]

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'teacher', 'is_published', 'created_at')
    list_filter = ('module', 'is_published', 'teacher')
    list_editable = ('is_published',)
    search_fields = ('title', 'description')
    exclude = ('slug',)
    inlines = [ChapterInline, EnrollmentInline]

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('name',)
    exclude = ('slug',)
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter', 'order')
    list_filter = ('chapter__course', 'chapter')
    search_fields = ('title', 'content')
    exclude = ('slug',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'created_at')
    list_filter = ('course', 'created_at')