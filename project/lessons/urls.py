from django.urls import path

from .views import LessonDetailView

urlpatterns = [
    path("lessons/<int:pk>", LessonDetailView.as_view(), name="lesson-detail"),
]
