from django.urls import path

from .views import TaskDetailView

urlpatterns = [
    path("tasks/<int:pk>", TaskDetailView.as_view(), name="task-detail"),
]
