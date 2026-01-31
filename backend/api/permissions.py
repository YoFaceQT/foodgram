from rest_framework import permissions


class AdminAuthorOrReadOnly(permissions.BasePermission):
    """Разграничение доступа, Автор и Админ или только чтение"""

    def has_permission(self, request, view):
        """
        Проверяем права на уровне запроса.
        Для создания рецепта пользователь должен быть авторизован.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.action == 'create':
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        """
        Проверяем права на уровне объекта.
        """
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or obj.author == request.user
        )
