from rest_framework import generics, permissions

from .models import Lesson
from .serializers import LessonSerializer


class LessonDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Lesson.objects.filter(is_published=True).select_related("course")
    serializer_class = LessonSerializer
