from django.urls import path

from .views import SubmitSolutionView

urlpatterns = [
    path("submit-solution", SubmitSolutionView.as_view(), name="submit-solution"),
]
