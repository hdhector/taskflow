#!/bin/bash
set -euo pipefail

echo "Iniciando despliegue de TaskFlow..."

# Verificar si existe .env, si no, crearlo desde .env.example
if [ ! -f .env ]; then
    echo "Archivo .env no encontrado"
    if [ -f .env.example ]; then
        echo "Creando .env desde .env.example..."
        cp .env.example .env
        echo "IMPORTANTE: Edita el archivo .env con tus valores antes de continuar"
        echo "Especialmente el SECRET_KEY debe ser cambiado en producción"
    else
        echo "Error: .env.example no encontrado"
        exit 1
    fi
else
    echo "Archivo .env encontrado"
fi

# Verificar si Docker está instalado y corriendo
if ! command -v docker &> /dev/null; then
    echo "Error: Docker no está instalado"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "Error: Docker no está corriendo"
    exit 1
fi

echo "Docker está instalado y corriendo"

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose no está instalado"
    exit 1
fi

# Usar docker-compose o docker compose según disponibilidad
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

echo "Docker Compose disponible"

# Construir y levantar los contenedores
echo "Construyendo contenedores..."
$COMPOSE_CMD build

echo "Levantando servicios..."
$COMPOSE_CMD up -d

echo "Despliegue completado exitosamente!"
echo "La aplicación está disponible en: http://localhost:8000"
echo "Para ver los logs: $COMPOSE_CMD logs -f"
echo "Para detener: $COMPOSE_CMD down"

