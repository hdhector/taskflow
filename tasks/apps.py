from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Configuración de la aplicación Tasks que gestiona tareas y comentarios."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
