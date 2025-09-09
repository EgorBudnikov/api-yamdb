from rest_framework import permissions


class AdminPerm(permissions.BasePermission):
    """Пермишен на проверку прав администратора."""

    def has_permission(self, request, view):
        """Проверка до создания объекта."""
        return request.user.is_authenticated and (
            request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Администратор или только чтение."""

    def has_permission(self, request, view):
        """Проверка до создания объекта."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and request.user.is_admin)


class IsAuthorModeratorAdminOrReadOnly(permissions.BasePermission):
    """
    Проверка прав пользователей.

    Чтение - для всех;
    Создание - только аутентифицированным пользователям;
    Изменение/удаление - автору, модератору, администратору, суперпользователю.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.role in ('moderator', 'admin')
            or request.user.is_superuser
        )
