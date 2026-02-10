from django.urls import path, include
from . import views

extra_patterns = [
    path('', views.CategoryListView.as_view(), name='category_list'),
    path('<slug:category_slug>/<str:course_name>/', views.ChapterListView.as_view(), name='chapter_list'),
    path(
        '<slug:category_slug>/<slug:course_name>/Chapter-<int:chapter_order>/<slug:lesson_slug>/',
        views.LessonDetailView.as_view(),
        name='lesson_detail'
    )
]

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('start-study/', include(extra_patterns)),
]