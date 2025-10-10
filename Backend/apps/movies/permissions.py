from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Пользователь должен быть администратором для выполнения
    небезопасных методов (POST, PUT, DELETE).
    Безопасные методы (GET, HEAD, OPTIONS) разрешены всем.
    """

    def has_permission(self, request, view):
        # Разрешаем читать всем пользователям
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешаем изменять только администраторам
        return request.user and request.user.is_staff