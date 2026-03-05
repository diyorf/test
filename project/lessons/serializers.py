from rest_framework import serializers

from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course",
            "course_title",
            "title",
            "content",
            "lesson_type",
            "order_index",
            "estimated_minutes",
            "is_published",
            "created_at",
            "updated_at",
        )
