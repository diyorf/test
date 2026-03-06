from django.contrib import admin

from .models import Course, Progress


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "instructor", "is_published", "created_at")
    list_filter = ("level", "is_published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "lesson", "task", "status", "completion_percent")
    list_filter = ("status", "course")
    search_fields = ("user__username", "course__title")
