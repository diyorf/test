from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RunCodeSerializer


class CodeEditorPageView(TemplateView):
    template_name = "code_editor.html"


class RunCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RunCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        source_code = serializer.validated_data["source_code"]
        # Placeholder response for now; real execution will be delegated to Docker runner worker.
        return Response(
            {
                "message": "Code accepted for execution.",
                "status": "queued",
                "preview": source_code[:120],
                "stdin": serializer.validated_data.get("stdin", ""),
            }
        )
