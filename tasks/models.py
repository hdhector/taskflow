from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
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
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["title"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.priority})"

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.DONE

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author_id} on task {self.task_id}"
