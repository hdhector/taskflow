from rest_framework.routers import DefaultRouter
from .views import TaskViewSet


# Router que genera automáticamente las URLs para operaciones CRUD de tareas
router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")  # Registra el ViewSet en /tasks/

urlpatterns = router.urls  # URLs generadas: /tasks/, /tasks/{id}/, /tasks/{id}/comments/