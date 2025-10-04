from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для пользователей."""

    list_display = (
        'email', 'username', 'first_name',
        'last_name', 'is_staff', 'is_active'
    )
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка для подписок."""

    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    ordering = ('user',)
