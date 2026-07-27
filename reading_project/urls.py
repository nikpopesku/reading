from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve


def serve_media(request, path):
    return serve(request, path, document_root=settings.MEDIA_ROOT)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("reading.urls")),
    path(f"{settings.MEDIA_URL.lstrip('/')}<path:path>", serve_media, name="media"),
]
