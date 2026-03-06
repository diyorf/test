from rest_framework import generics, permissions

from .models import Course
from .serializers import CourseSerializer


class CourseListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Course.objects.filter(is_published=True).select_related("instructor")
    serializer_class = CourseSerializer


class CourseDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = Course.objects.filter(is_published=True).select_related("instructor")
    serializer_class = CourseSerializer
