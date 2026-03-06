from django.conf import settings
from django.db import models


class Submission(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"
        ERROR = "error", "Error"
        TIMEOUT = "timeout", "Timeout"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions")
    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE, related_name="submissions")
    source_code = models.TextField()
    language = models.CharField(max_length=20, default="python")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    score = models.PositiveIntegerField(default=0)
    passed_tests = models.PositiveIntegerField(default=0)
    total_tests = models.PositiveIntegerField(default=0)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)
    execution_time_ms = models.PositiveIntegerField(default=0)
    memory_used_kb = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"Submission #{self.id} - {self.user.username} - {self.task.title}"
