from django.urls import include, path


urlpatterns = [
    path("users/", include("api.users.urls")),
    path("", include("api.recipes.urls")),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
