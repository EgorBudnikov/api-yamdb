from rest_framework import permissions


class AdminPerm(permissions.BasePermission):
    """Пермишен на проверку прав администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser)

    def has_objects_permission(self, request, view, obj):
        """Проверка после создания объекта."""
        return request.user.is_admin or request.user.is_superuser
