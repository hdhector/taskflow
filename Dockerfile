# Dockerfile for TaskFlow
FROM python:3.12-slim

# Variables de entorno básicas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV PYTHONPATH=/app

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc postgresql-client curl \
    && rm -rf /var/lib/apt/lists/*

# Crear un usuario no root
RUN useradd -m -s /bin/bash taskflow

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm -rf ~/.cache/pip

# Copiar el proyecto al contenedor con el propietario correcto
COPY --chown=taskflow:taskflow . .

# Crear directorio para archivos estáticos con permisos correctos
RUN mkdir -p /app/staticfiles && \
    chown -R taskflow:taskflow /app/staticfiles && \
    chmod 755 /app/staticfiles

# Dar permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh

# Cambiar al usuario no root
USER taskflow

# Exponer puerto
EXPOSE 8000

# Healthcheck (opcional)
HEALTHCHECK CMD curl -f http://localhost:8000/ || exit 1

# Entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
