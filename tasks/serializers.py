from rest_framework import serializers
from django.db.models import Q
from .models import Task, Comment

class CommentSerializer(serializers.ModelSerializer):
    """Serializa comentarios mostrando el username del autor en lugar del ID."""
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]


class TaskListSerializer(serializers.ModelSerializer):
    """Serializador ligero para listados que solo incluye campos esenciales (sin descripción ni comentarios)."""
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Task
        fields = ["id", "title", "priority", "status", "owner", "created_at"]


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializador completo que incluye todos los campos de la tarea junto con sus comentarios."""
    owner = serializers.ReadOnlyField(source="owner.username")
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "priority", "status",
            "owner", "created_at", "updated_at", "comments"
        ]

    # Validación de negocio: máx. 5 activas por usuario
    def validate(self, attrs):
        """Valida que un usuario no tenga más de 5 tareas activas (no completadas) simultáneamente."""
        request = self.context.get("request")
        user = request.user if request else None
        if not user or not user.is_authenticated:
            return attrs

        # Si es create, el objeto aún no existe; si es update, excluir self.instance
        qs = Task.objects.filter(owner=user).exclude(status=Task.Status.DONE)  # Tareas activas del usuario
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)  # Excluir la tarea actual si se está actualizando

        # Si la nueva data mantiene/crea una tarea activa:
        new_status = attrs.get("status", getattr(self.instance, "status", Task.Status.PENDING))
        if new_status != Task.Status.DONE and qs.count() >= 5:
            raise serializers.ValidationError(
                {"detail": "Máximo 5 tareas activas por usuario."}
            )
        return attrs

    def create(self, validated_data):
        """Asigna automáticamente el usuario autenticado como propietario al crear una nueva tarea."""
        request = self.context.get("request")
        validated_data["owner"] = request.user
        return super().create(validated_data)