from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Task, Comment
from .serializers import (
    TaskListSerializer, TaskDetailSerializer, CommentSerializer
)
from .permissions import IsOwnerOrReadOnly # Solo Owner puede editar


# Create your views here.
class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet que proporciona operaciones CRUD completas para tareas mediante API REST."""
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority"]
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]

    def get_queryset(self):
        """Retorna todas las tareas; los permisos de edición se controlan en IsOwnerOrReadOnly."""
        # # Solo las tareas del usuario autenticado
        # return Task.objects.filter(owner=self.request.user).select_related("owner")
        # Permitir ver todas las tareas, pero filtrar permisos en IsOwnerOrReadOnly
        return Task.objects.all()

    def get_serializer_class(self):
        """Usa TaskListSerializer para el listado (campos reducidos) y TaskDetailSerializer para el resto (con comentarios)."""
        if self.action in ["list"]:
            return TaskListSerializer
        return TaskDetailSerializer

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        """Endpoint personalizado para listar (GET) o crear (POST) comentarios de una tarea específica."""
        task = self.get_object()  # respeta permisos y filtro de owner

        if request.method == "GET":
            # Retornar todos los comentarios de la tarea
            serializer = CommentSerializer(task.comments.all(), many=True)
            return Response(serializer.data)

        # POST: crear comentario
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Crear comentario con el usuario autenticado como autor
        Comment.objects.create(
            task=task,
            author=request.user,
            content=serializer.validated_data["content"],
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)