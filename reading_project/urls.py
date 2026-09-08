from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.static import serve


def serve_media(request, path):
    return serve(request, path, document_root=settings.MEDIA_ROOT)


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots-txt",
    ),
    path("", include("reading.urls")),
    path(f"{settings.MEDIA_URL.lstrip('/')}<path:path>", serve_media, name="media"),
]
