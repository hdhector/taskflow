from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from tasks.models import Task, Comment

User = get_user_model()
# Create your tests here.


class TaskAPITestCase(APITestCase):

    def setUp(self):
        """Se ejecuta antes de cada test."""
        self.user = User.objects.create_user(username="user1", password="pass1234")
        self.client = APIClient()
        # Obtener token JWT
        response = self.client.post(reverse("token_obtain_pair"), {
            "username": "user1",
            "password": "pass1234"
        })
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_task(self):
        """Debe crear una tarea correctamente"""
        data = {"title": "Tarea de prueba", "description": "Probando creación"}
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().owner, self.user)

    def test_list_tasks(self):
        """Debe listar las tareas del usuario autenticado"""
        Task.objects.create(title="T1", owner=self.user)
        Task.objects.create(title="T2", owner=self.user)
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

    def test_limit_active_tasks(self):
        """Debe restringir a 5 tareas activas"""
        for i in range(5):
            Task.objects.create(title=f"Tarea {i}", owner=self.user)
        data = {"title": "Exceso", "description": "6ta tarea"}
        response = self.client.post("/api/tasks/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Máximo 5 tareas activas", str(response.data))

    def test_comments_on_task(self):
        """Debe permitir agregar y listar comentarios"""
        task = Task.objects.create(title="Task con comentarios", owner=self.user)
        # Crear comentario
        data = {"content": "Primer comentario"}
        response = self.client.post(f"/api/tasks/{task.id}/comments/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)

        # Listar comentarios
        response = self.client.get(f"/api/tasks/{task.id}/comments/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_only_owner_can_update(self):
        """Solo el dueño puede modificar la tarea"""
        task = Task.objects.create(title="Tarea protegida", owner=self.user)

        # Otro usuario
        other = User.objects.create_user(username="intruso", password="pass1234")
        resp = self.client.post(reverse("token_obtain_pair"), {
            "username": "intruso",
            "password": "pass1234"
        })
        token = resp.data["access"]
        intruder = APIClient()
        intruder.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {"title": "Intento de edición"}
        response = intruder.put(f"/api/tasks/{task.id}/", data, format="json")
        self.assertEqual(response.status_code, 403)