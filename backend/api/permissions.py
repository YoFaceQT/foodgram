from rest_framework import permissions


class IsAdminAuthorOrReadOnly(permissions.BasePermission):
    """Разграничение доступа, Автор и Админ или только чтение"""

    def has_permission(self, request, view):
        """
        Проверяем права на уровне запроса.
        Для создания рецепта пользователь должен быть авторизован.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """
        Проверяем права на уровне объекта.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
