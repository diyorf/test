from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "lesson",
            "lesson_title",
            "title",
            "description",
            "starter_code",
            "solution_template",
            "input_format",
            "output_format",
            "constraints",
            "difficulty",
            "max_score",
            "time_limit_ms",
            "memory_limit_mb",
            "is_published",
            "created_at",
            "updated_at",
        )
