from rest_framework import permissions


class AdminAuthorOrReadOnly(permissions.BasePermission):
    """Разграничение доступа, Автор и Админ или только чтение"""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser or obj.author == request.user
        )
