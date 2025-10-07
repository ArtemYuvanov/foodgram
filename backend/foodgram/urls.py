from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.recipes.short_link_views import short_link_redirect

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("s/<int:pk>/", short_link_redirect, name="short_link"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
