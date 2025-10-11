from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """
    Доступ к объекту только автору, администратору или на чтение для остальных.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or request.user.is_staff
            or obj.author == request.user
        )
