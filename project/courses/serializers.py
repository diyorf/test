from rest_framework import serializers

from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    instructor_username = serializers.CharField(source="instructor.username", read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "level",
            "is_published",
            "instructor",
            "instructor_username",
            "created_at",
            "updated_at",
        )
