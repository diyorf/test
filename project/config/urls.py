from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView


def health_check(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("", RedirectView.as_view(url="/homepage", permanent=False), name="root-redirect"),
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
    path("", include("users.urls")),
    path("", include("courses.urls")),
    path("", include("lessons.urls")),
    path("", include("tasks.urls")),
    path("", include("submissions.urls")),
    path("", include("code_runner.urls")),
    path("homepage", TemplateView.as_view(template_name="pages/homepage.html"), name="homepage"),
    path("dashboard", TemplateView.as_view(template_name="pages/dashboard.html"), name="dashboard"),
    path("course", TemplateView.as_view(template_name="pages/course_page.html"), name="course-page"),
    path("lesson", TemplateView.as_view(template_name="pages/lesson_page.html"), name="lesson-page"),
    path("coding", TemplateView.as_view(template_name="pages/coding_page.html"), name="coding-page"),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
