from django.contrib import admin

from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "lesson_type", "order_index", "is_published")
    list_filter = ("lesson_type", "is_published", "course")
    search_fields = ("title", "course__title")
