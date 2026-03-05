from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_courses",
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="enrolled_courses",
        blank=True,
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class Progress(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress_items")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="progress_records")
    lesson = models.ForeignKey(
        "lessons.Lesson", on_delete=models.CASCADE, related_name="progress_records", null=True, blank=True
    )
    task = models.ForeignKey(
        "tasks.Task", on_delete=models.CASCADE, related_name="progress_records", null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    completion_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course", "lesson", "task"],
                name="unique_user_course_lesson_task_progress",
            )
        ]

    def __str__(self) -> str:
        target = self.task or self.lesson or self.course
        return f"{self.user.username} - {target} - {self.status}"
