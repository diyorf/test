from django.db import models


class Task(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    lesson = models.ForeignKey("lessons.Lesson", on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField()
    starter_code = models.TextField(blank=True)
    solution_template = models.TextField(blank=True)
    input_format = models.TextField(blank=True)
    output_format = models.TextField(blank=True)
    constraints = models.TextField(blank=True)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.EASY)
    max_score = models.PositiveIntegerField(default=100)
    time_limit_ms = models.PositiveIntegerField(default=2000)
    memory_limit_mb = models.PositiveIntegerField(default=128)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["lesson", "id"]

    def __str__(self) -> str:
        return f"{self.title} ({self.difficulty})"


class TestCase(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="test_cases")
    input_data = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=True)
    weight = models.PositiveIntegerField(default=1)
    order_index = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["task", "order_index", "id"]
        unique_together = ("task", "order_index")

    def __str__(self) -> str:
        visibility = "hidden" if self.is_hidden else "public"
        return f"{self.task.title} test #{self.order_index} ({visibility})"
