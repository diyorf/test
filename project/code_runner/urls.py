from django.urls import path

from .views import CodeEditorPageView, RunCodeView

urlpatterns = [
    path("editor", CodeEditorPageView.as_view(), name="code-editor-page"),
    path("run-code", RunCodeView.as_view(), name="run-code"),
]
