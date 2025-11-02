from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Task(models.Model):
    """Modelo que representa una tarea del sistema con título, descripción, prioridad, estado y propietario."""
    
    class Priority(models.TextChoices):
        """Opciones de prioridad: baja, media o alta."""
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        """Estados posibles de una tarea: pendiente, en progreso o completada."""
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tasks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # Ordenar por fecha descendente (más recientes primero)
        indexes = [
            models.Index(fields=["owner", "status"]),  # Índice compuesto para consultas por propietario y estado
            models.Index(fields=["priority"]),  # Índice para filtros por prioridad
            models.Index(fields=["title"]),  # Índice para búsquedas por título
        ]

    def __str__(self):
        return f"{self.title} ({self.priority})"

    @property
    def is_active(self) -> bool:
        """Retorna True si la tarea está completada (DONE), False en caso contrario."""
        return self.status == self.Status.DONE

class Comment(models.Model):
    """Modelo que representa un comentario asociado a una tarea, con autor y fecha de creación."""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]  # Ordenar por fecha ascendente (más antiguos primero)

    def __str__(self):
        return f"Comment by {self.author_id} on task {self.task_id}"
