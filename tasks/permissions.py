from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Permiso que permite lectura a todos los usuarios autenticados y escritura solo al propietario del objeto."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            # Solo lectura permitida si se quisiera listar globalmente (en nuestro caso filtramos por owner)
            return True  # GET, HEAD, OPTIONS permitidos para todos
        # Para métodos de escritura (POST, PUT, PATCH, DELETE) solo el propietario puede modificar
        return getattr(obj, "owner_id", None) == request.user.id