from rest_framework import serializers

from .models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    failed_tests = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = (
            "id",
            "user",
            "task",
            "source_code",
            "language",
            "status",
            "score",
            "passed_tests",
            "failed_tests",
            "total_tests",
            "stdout",
            "stderr",
            "execution_time_ms",
            "memory_used_kb",
            "submitted_at",
            "evaluated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "score",
            "passed_tests",
            "failed_tests",
            "total_tests",
            "stdout",
            "stderr",
            "execution_time_ms",
            "memory_used_kb",
            "submitted_at",
            "evaluated_at",
            "user",
        )

    def get_failed_tests(self, obj):
        return max(obj.total_tests - obj.passed_tests, 0)


class SubmitSolutionSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    source_code = serializers.CharField()
    language = serializers.CharField(default="python")
