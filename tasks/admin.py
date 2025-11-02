from django.contrib import admin
from .models import Task, Comment
# Register your models here.

class CommentInline(admin.TabularInline):
    model = Comment
    fk_name = "task" #reforzar vinculo
    extra = 1  # Muestra un campo vacío adicional
    verbose_name_plural = "comments"
    fields = ("content", "author","created_at")
    readonly_fields = ("author","created_at",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "priority", "created_at")
    search_fields = ("title", "description")
    list_filter = ("status", "priority", "owner")
    readonly_fields = ("created_at", "updated_at", "owner")
    inlines = [CommentInline]

    def save_model(self, request, obj, form, change):
        # Asigna automáticamente el usuario creador
        if not obj.pk:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Asigna automáticamente el autor del comentario
        y asegura que el comentario esté vinculado a la tarea.
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Comment):
                instance.author = request.user
                instance.task = form.instance
                instance.save()
        formset.save_m2m()

    def has_change_permission(self, request, obj=None):
        # Permitir entrar a la vista de detalle de cualquier tarea
        if obj is None:
            return True

        # Si no es el dueño, permitir solo lectura (sin modificar)
        if obj.owner != request.user:
            # Retorna True : permite acceder al formulario
            # pero los campos serán solo lectura (definidos abajo)
            return True

        # El dueño sí puede editar normalmente
        return True

    def get_readonly_fields(self, request, obj=None):
        """
        Solo el dueño o el superusuario pueden editar la tarea.
        Los demás usuarios verán todos los campos como solo lectura.
        """
        if obj and obj.owner != request.user and not request.user.is_superuser:
            base_fields = [f.name for f in self.model._meta.fields]
            return base_fields
        return self.readonly_fields
