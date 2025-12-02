FROM python:3.12-slim

# 1. Dependencias del sistema
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT="/app/.venv" \
    # Esto asegura que uv compile bytecode para arranque más rápido
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# CAMBIO AQUÍ: Agregamos la copia de la carpeta src
COPY pyproject.toml ruff.toml README.md ./
COPY src ./src

# Ahora sí, al sincronizar, uv encontrará el código en ./src
RUN uv sync

CMD ["/bin/bash"]
