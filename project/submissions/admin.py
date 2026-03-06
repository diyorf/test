from django.contrib import admin

from .models import Submission


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "task", "status", "score", "submitted_at")
    list_filter = ("status", "language")
    search_fields = ("user__username", "task__title")
