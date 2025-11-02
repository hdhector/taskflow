from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from tasks.models import Task, Comment
from django.test import TestCase


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


class TaskAdminTestCase(TestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser("admin", "admin@test.com", "adminpass")

        # staff (no superuser)
        self.owner = User.objects.create_user(username="owner", password="pass1234", is_staff=True)
        self.other = User.objects.create_user(username="other", password="pass1234", is_staff=True)

        #Permisos para que el admin acepte crear/editar inlines Comment
        add_comment = Permission.objects.get(codename="add_comment")
        change_comment = Permission.objects.get(codename="change_comment")
        view_comment = Permission.objects.get(codename="view_comment")

        self.owner.user_permissions.add(add_comment, change_comment, view_comment)
        self.other.user_permissions.add(add_comment, change_comment, view_comment)

        self.task = Task.objects.create(title="Tarea de prueba", owner=self.owner)


    #Pruebas sobre permisos de edición
    def test_owner_can_edit_own_task_in_admin(self):
        """El dueño debe poder editar su propia tarea."""
        self.client.login(username="owner", password="pass1234")

        url = reverse("admin:tasks_task_change", args=[self.task.id])
        post_data = {
            "title": "Tarea modificada por el dueño",
            "description": "Actualizada correctamente",
            "owner": self.owner.id,
            "status": self.task.status,
            "priority": self.task.priority,
            "comments-TOTAL_FORMS": "0",
            "comments-INITIAL_FORMS": "0",
            "comments-MIN_NUM_FORMS": "0",
            "comments-MAX_NUM_FORMS": "1000",
        }

        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Tarea modificada por el dueño")

    def test_other_user_can_only_view_task(self):
        """Un usuario ajeno puede ver la tarea pero no modificarla."""
        self.client.login(username="other", password="pass1234")

        url = reverse("admin:tasks_task_change", args=[self.task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "readonly")

        # Intento de modificación
        post_data = {
            "title": "Intento de cambio no permitido",
            "description": "No debería guardar",
            "owner": self.owner.id,
            "status": self.task.status,
            "priority": self.task.priority,
            "comments-TOTAL_FORMS": "0",
            "comments-INITIAL_FORMS": "0",
            "comments-MIN_NUM_FORMS": "0",
            "comments-MAX_NUM_FORMS": "1000",
        }

        response = self.client.post(url, post_data, follow=True)
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.title, "Intento de cambio no permitido")

    def test_superuser_can_edit_any_task(self):
        """El superusuario puede editar cualquier tarea."""
        self.client.login(username="admin", password="adminpass")

        url = reverse("admin:tasks_task_change", args=[self.task.id])
        post_data = {
            "title": "Editada por superuser",
            "description": "El admin puede todo",
            "owner": self.owner.id,
            "status": self.task.status,
            "priority": self.task.priority,
            "comments-TOTAL_FORMS": "0",
            "comments-INITIAL_FORMS": "0",
            "comments-MIN_NUM_FORMS": "0",
            "comments-MAX_NUM_FORMS": "1000",
        }

        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Editada por superuser")

    #Pruebas sobre comentarios (inline)
    def test_owner_can_add_comment(self):
        """El dueño puede agregar comentarios a su propia tarea."""
        self.client.login(username="owner", password="pass1234")

        url = reverse("admin:tasks_task_change", args=[self.task.id])
        post_data = {
            "title": self.task.title,
            "description": self.task.description,
            "owner": self.task.owner.id,
            "status": self.task.status,
            "priority": self.task.priority,
            "comments-TOTAL_FORMS": "1",
            "comments-INITIAL_FORMS": "0",
            "comments-MIN_NUM_FORMS": "0",
            "comments-MAX_NUM_FORMS": "1000",
            "comments-0-id": "",
            "comments-0-task": str(self.task.id),
            "comments-0-content": "Comentario del owner",
        }

        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(content__icontains="Comentario del owner").exists())

    def test_other_user_can_add_comment_but_not_edit_task(self):
        """Otro usuario puede comentar pero no editar la tarea."""
        self.client.login(username="other", password="pass1234")

        url = reverse("admin:tasks_task_change", args=[self.task.id])
        post_data = {
            "title": self.task.title,
            "description": self.task.description,
            "owner": self.task.owner.id,
            "status": self.task.status,
            "priority": self.task.priority,
            "comments-TOTAL_FORMS": "1",
            "comments-INITIAL_FORMS": "0",
            "comments-MIN_NUM_FORMS": "0",
            "comments-MAX_NUM_FORMS": "1000",
            "comments-0-id": "",  # necesario
            "comments-0-task": str(self.task.id),
            "comments-0-content": "Comentario desde otro usuario",
        }

        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(content__icontains="Comentario desde otro usuario").exists())

        # Aseguramos que el título no se modificó
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Tarea de prueba")

    #Pruebas sobre acceso al listado
    def test_admin_task_list_access(self):
        """Todos los usuarios autenticados pueden acceder al listado del admin."""
        self.client.login(username="other", password="pass1234")
        url = reverse("admin:tasks_task_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tarea de prueba")

