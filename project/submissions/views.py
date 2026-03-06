from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.models import Task

from .models import Submission
from .serializers import SubmissionSerializer, SubmitSolutionSerializer
from .services import grade_submission


class SubmitSolutionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SubmitSolutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = Task.objects.filter(pk=serializer.validated_data["task_id"], is_published=True).first()
        if not task:
            return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        submission = Submission.objects.create(
            user=request.user,
            task=task,
            source_code=serializer.validated_data["source_code"],
            language=serializer.validated_data.get("language", "python"),
            status=Submission.Status.QUEUED,
            total_tests=task.test_cases.count(),
        )

        graded_submission = grade_submission(submission)
        payload = SubmissionSerializer(graded_submission).data

        return Response(
            {
                "message": "Solution graded successfully.",
                "submission": payload,
                "passed_tests": payload["passed_tests"],
                "failed_tests": payload["failed_tests"],
                "execution_time_ms": payload["execution_time_ms"],
            },
            status=status.HTTP_201_CREATED,
        )
