from django.contrib import admin

from .models import Task, TestCase


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "difficulty", "max_score", "is_published")
    list_filter = ("difficulty", "is_published")
    search_fields = ("title", "description")


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ("task", "order_index", "is_hidden", "weight")
    list_filter = ("is_hidden",)
    search_fields = ("task__title",)
