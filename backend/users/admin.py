from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


class UserFilter(AutocompleteFilter):
    title = "Пользователь"
    field_name = "user"


class AuthorFilter(AutocompleteFilter):
    title = "Автор"
    field_name = "author"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователей."""

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    list_display_links = ("email", "username")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("username",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка для подписок."""

    list_display = ("user", "author")
    list_display_links = ("user",)
    search_fields = ("user__username", "author__username")
    list_filter = (UserFilter, AuthorFilter)
    ordering = ("user",)

    def get_queryset(self, request):
        """Оптимизация запросов."""
        return (
            super()
            .get_queryset(request)
            .select_related("user", "author")
        )
