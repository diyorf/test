from rest_framework import generics, permissions

from .models import Task
from .serializers import TaskSerializer


class TaskDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Task.objects.filter(is_published=True).select_related("lesson")
    serializer_class = TaskSerializer
