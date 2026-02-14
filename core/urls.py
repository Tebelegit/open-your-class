from django.urls import path, include
from . import views

extra_patterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('<slug:category_slug>/<slug:module_slug>/courses/', views.CourseListView.as_view(), name='course_list'),
    path('<slug:category_slug>/<slug:module_slug>/courses/<slug:course_slug>/chapters/', views.ChapterListView.as_view(), name='chapter_list'),
    path('<slug:category_slug>/<slug:module_slug>/courses/<slug:course_slug>/<slug:chapter_slug>/<slug:lesson_slug>/', 
        views.LessonDetailView.as_view(), name='lesson_detail'),
]

profile_patterns = [
    path('', views.dashboard_view, name='dashboard_control'),
    path('teacher/', views.dashboard_teacher_view, name='dashboard_teacher'),
    path('student/', views.dashboard_student_view, name='dashboard_student')
]

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('start-study/', include(extra_patterns)),
    path('create-course/', views.CourseCreateView.as_view(), name='create_course'),
    path('accounts/profile/', include(profile_patterns)),

    # auth
    path('account/register/', views.RegisterView.as_view(), name='register'),
]