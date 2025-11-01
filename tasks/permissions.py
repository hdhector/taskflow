from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            # Solo lectura permitida si se quisiera listar globalmente (en nuestro caso filtramos por owner)
            return True
        return getattr(obj, "owner_id", None) == request.user.id