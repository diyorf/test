from django.db import models


class Lesson(models.Model):
    class LessonType(models.TextChoices):
        THEORY = "theory", "Theory"
        PRACTICE = "practice", "Practice"

    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField()
    lesson_type = models.CharField(max_length=20, choices=LessonType.choices, default=LessonType.THEORY)
    order_index = models.PositiveIntegerField(default=1)
    estimated_minutes = models.PositiveIntegerField(default=15)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["course", "order_index"]
        unique_together = ("course", "order_index")

    def __str__(self) -> str:
        return f"{self.course.title} - {self.title}"
