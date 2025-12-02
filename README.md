# Agente de Tres en Raya con Algoritmo Minimax

Este repositorio contiene el desarrollo de un agente inteligente capaz de jugar al "Tres en Raya" (Tic-Tac-Toe) contra un oponente humano. El proyecto utiliza el algoritmo **Minimax** para la toma de decisiones y **Pygame** para la interfaz gráfica.

**Materia:** Inteligencia Artificial  
**Institución:** Universidad Nacional Experimental de Guayana (UNEG)  
**Profesor:** Manuel Paniccia  
**Fecha de entrega:** 10 de Diciembre de 2025

---

## 🛠️ Tecnologías y Entorno

El proyecto está contenerizado para garantizar que funcione en cualquier máquina Linux sin problemas de dependencias.

- **Lenguaje:** Python 3.12+
- **Gestor de Paquetes:** `uv` (Astral)
- **Interfaz Gráfica:** Pygame
- **Cálculo Matemático:** Numpy
- **Contenerización:** Podman + Podman Compose
- **Calidad de Código:** Ruff

---

Claro, aquí tienes la sección `## 🚀 Instalación y Ejecución` del `README.md` completamente actualizada para reflejar el uso del `Makefile`. Es mucho más limpia y fácil de seguir.

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
-   Tener instalado `podman` y `podman-compose` en un sistema Linux.
-   Tener `make` instalado (generalmente viene por defecto).

### 1. Configuración Inicial (Solo la primera vez)

1.  **Clonar el repositorio:**
    ```bash
    git clone <tu-repo-url>
    cd agente-minimax-tictactoe
    ```

2.  **Construir el entorno:**
    Este único comando construirá la imagen de Podman, levantará el contenedor e instalará todas las dependencias necesarias.
    ```bash
    make build
    ```

### 2. Flujo de Trabajo Diario

-   **Ejecutar el Juego:**
    Este comando se encarga de dar los permisos a la pantalla y lanzar la aplicación.
    ```bash
    make run
    ```

-   **Entrar al contenedor (Shell):**
    Para depurar o ejecutar comandos manualmente.
    ```bash
    make shell
    ```

-   **Detener el entorno:**
    Apaga y elimina el contenedor.
    ```bash
    make stop
    ```

-   **Ver todos los comandos disponibles:**
    Muestra una lista de todos los atajos y su descripción.
    ```bash
    make
    ```

---

## 📂 Estructura del Proyecto

```text
/
├── compose.yml       # Configuración del contenedor y volúmenes
├── Dockerfile        # Definición de la imagen de sistema (Python + SDL)
├── pyproject.toml    # Dependencias del proyecto (uv)
├── ruff.toml         # Configuración de linter
├── README.md         # Documentación
└── src/
    └── main.py       # Punto de entrada y lógica del juego
```
---

## 🔧 Solución de Problemas Comunes

### 1. `ModuleNotFoundError: No module named 'numpy'`
**Causa:** El volumen montado desde el host sobrescribió la carpeta `.venv` del contenedor.
**Solución:** Ejecuta `podman exec -it tictactoe_dev uv sync` para reinstalar las librerías en el volumen compartido.

### 2. `pygame.error: No video mode has been set` o Pantalla negra
**Causa:** El contenedor no tiene permiso para pintar en tu pantalla.
**Solución:**
1. Asegúrate de haber ejecutado `xhost +local:` en tu terminal host.
2. Verifica que la variable `DISPLAY` se esté pasando en el `compose.yml`.

### 3. `Error: no space left on device`
**Causa:** Podman Rootless llenó el espacio asignado en `/home` debido a múltiples builds fallidos.
**Solución:**
1. Limpiar imágenes basura: `podman system prune -a --volumes`.
2. Verificar espacio en disco con `df -h`.

### 4. `Error: short-name "..." did not resolve`
**Causa:** Falló el `build` de la imagen, por lo que Podman intenta buscarla en internet y falla.
**Solución:** Revisa los errores del Dockerfile y corre `podman-compose up -d --build` hasta que termine con éxito.
```


proyecto1/
└── src/
    ├── __init__.py         # (Opcional pero buena práctica)
    |
    ├── ai/
    │   ├── __init__.py     # Marca 'ai' como un paquete
    │   └── minimax.py      # Aquí vivirá toda la lógica del algoritmo Minimax
    |
    ├── game_logic/
    │   ├── __init__.py     # Marca 'game_logic' como un paquete
    │   └── board.py        # Lógica del tablero: mover, verificar ganador, etc.
    |
    ├── gui/
    │   ├── __init__.py     # Marca 'gui' como un paquete
    │   └── renderer.py     # Funciones para dibujar el tablero, las X/O, botones, etc.
    |
    ├── config.py           # Constantes: colores, tamaños de ventana, etc.
    |
    └── main.py             # El director de orquesta
