from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task, Comment
from faker import Faker
import random

class Command(BaseCommand):
    help = "Carga datos de prueba (usuarios, tareas y comentarios) usando Faker"

    def handle(self, *args, **options):
        fake = Faker("es_ES")
        User = get_user_model()

        self.stdout.write(self.style.MIGRATE_HEADING("Generando datos de prueba..."))

        # --- Crear usuarios ---
        users = []
        for _ in range(5):
            username = fake.user_name()
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": fake.email()}
            )
            user.set_password("demo123")
            user.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"{len(users)} usuarios creados."))

        # --- Crear tareas ---
        priorities = [Task.Priority.LOW, Task.Priority.MEDIUM, Task.Priority.HIGH]
        statuses = [Task.Status.PENDING, Task.Status.IN_PROGRESS, Task.Status.DONE]

        tasks = []
        for _ in range(20):
            owner = random.choice(users)
            task = Task.objects.create(
                title=fake.sentence(nb_words=4),
                description=fake.paragraph(nb_sentences=3),
                priority=random.choice(priorities),
                status=random.choice(statuses),
                owner=owner,
            )
            tasks.append(task)
        self.stdout.write(self.style.SUCCESS(f" {len(tasks)} tareas creadas."))

        # --- Crear comentarios ---
        total_comments = 0
        for task in random.sample(tasks, k=15):  # solo algunas tareas con comentarios
            for _ in range(random.randint(1, 3)):
                Comment.objects.create(
                    task=task,
                    author=random.choice(users),
                    content=fake.sentence(nb_words=10)
                )
                total_comments += 1

        self.stdout.write(self.style.SUCCESS(f"  {total_comments} comentarios generados."))
        self.stdout.write(self.style.SUCCESS("Carga de datos completada correctamente."))
