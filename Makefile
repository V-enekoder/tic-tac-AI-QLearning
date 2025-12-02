CONTAINER_NAME = tictactoe_dev

# --- Targets ---

# Declara que estos targets no son archivos, para que 'make' siempre los ejecute.
.PHONY: help build start stop run install shell lint format clean prune

.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "Makefile de Ayuda para el Proyecto Tres en Raya"
	@echo "------------------------------------------------"
	@echo "Uso: make [target]"
	@echo ""
	@echo "🎯 Targets Principales:"
	@printf "  \033[36m%-15s\033[0m %s\n" "build" "Construye la imagen y levanta el contenedor por primera vez."
	@printf "  \033[36m%-15s\033[0m %s\n" "start" "Inicia el contenedor si está detenido (sin reconstruir)."
	@printf "  \033[36m%-15s\033[0m %s\n" "stop" "Detiene y elimina el contenedor y la red."
	@printf "  \033[36m%-15s\033[0m %s\n" "run" "Ejecuta la aplicación principal (src/main.py)."
	@echo ""
	@echo "🛠️ Targets de Desarrollo:"
	@printf "  \033[36m%-15s\033[0m %s\n" "install" "Instala/sincroniza las dependencias de pyproject.toml."
	@printf "  \033[36m%-15s\033[0m %s\n" "shell" "Abre una terminal interactiva (bash) dentro del contenedor."
	@printf "  \033[36m%-15s\033[0m %s\n" "lint" "Revisa el código en busca de errores con Ruff."
	@printf "  \033[36m%-15s\033[0m %s\n" "format" "Formatea el código automáticamente con Ruff."
	@echo ""
	@echo "🧹 Targets de Limpieza:"
	@printf "  \033[36m%-15s\033[0m %s\n" "prune" "¡CUIDADO! Elimina TODAS las imágenes, contenedores y volúmenes no usados de Podman."
	@printf "pre-commit-install "Para configurar pre commits""
	@echo ""

build: ## Construye y levanta el contenedor desde cero
	@echo "-> Construyendo y levantando el entorno de desarrollo..."
	@podman-compose up -d --build
	@make install

start: ## Inicia el contenedor si ya existe
	@echo "-> Iniciando el contenedor..."
	@podman-compose up -d

stop: ## Detiene y elimina el contenedor
	@echo "-> Deteniendo el contenedor..."
	@podman-compose down

run: ## Ejecuta el script principal
	@echo "-> Concediendo acceso a la pantalla (X11)..."
	@xhost +local:
	@echo "-> Ejecutando el juego..."
	@podman exec -it $(CONTAINER_NAME) uv run src/main.py

install: ## Sincroniza las dependencias
	@echo "-> Sincronizando dependencias con uv..."
	@podman exec -it $(CONTAINER_NAME) uv sync

shell: ## Entra al contenedor
	@echo "-> Abriendo terminal en el contenedor '$(CONTAINER_NAME)'..."
	@podman exec -it $(CONTAINER_NAME) /bin/bash

lint: ## Revisa el código
	@echo "-> Revisando el código con Ruff..."
	@podman exec -it $(CONTAINER_NAME) ruff check .

format: ## Formatea el código
	@echo "-> Formateando el código con Ruff..."
	@podman exec -it $(CONTAINER_NAME) ruff format .

prune: ## Limpieza profunda de Podman
	@echo "-> Limpiando el sistema Podman (imágenes, contenedores, volúmenes)..."
	@podman system prune -a --volumes --force
# ... (otros targets)
pre-commit-install: ## Instala los git hooks en tu repositorio local
	@echo "-> Instalando git hooks con pre-commit..."
	@podman exec -it $(CONTAINER_NAME) pre-commit install
