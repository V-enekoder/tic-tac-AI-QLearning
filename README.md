
# Meta-Optimización de Q-Learning: La Carrera a la Perfección

Este repositorio contiene un estudio avanzado de Aprendizaje por Refuerzo (Reinforcement Learning) aplicado al "Tres en Raya". El objetivo no es solo crear un agente inteligente, sino encontrar los parámetros de aprendizaje ($\alpha$ y $\gamma$) más eficientes mediante **Grid Search** y **Algoritmos Genéticos**, evaluándolos a través de un sistema de **Rating Elo**.

**Materia:** Inteligencia Artificial  
**Institución:** Universidad Nacional Experimental de Guayana (UNEG)  
**Profesor:** Manuel Paniccia  
**Fecha de entrega:** 31 de Enero de 2026

---

## 🔬 Descripción del Proyecto

A diferencia de un enfoque tradicional (Minimax), este proyecto implementa **Q-Learning Tabular** donde el agente aprende desde cero a través de la experiencia. El núcleo del proyecto es la comparación de agentes mediante un torneo genético, para obtener los mejores hiperparámetros de entrenamiento.

---

## 🛠️ Tecnologías y Entorno

El proyecto está contenerizado para garantizar consistencia en cualquier entorno Linux (probado en Linux Mint / Fedora).

- **Lenguaje:** Python 3.12+
- **Gestor de Paquetes:** `uv` (Astral)
- **Interfaz Gráfica:** Pygame (para visualización de duelos)
- **Cálculo Matemático:** Numpy
- **Contenerización:** Podman + Podman Compose
- **Calidad de Código:** Ruff
- **Persistencia:** Pickle (para almacenamiento de Q-Tables)

---

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Tener instalado `podman` y `podman-compose`.
- Tener `make` instalado.

### 1. Configuración Inicial
```bash
git clone https://github.com/V-enekoder/qlearning-tictactoe.git
cd qlearning-tictactoe
make build
```

### 2. Comandos del Makefile
- **`make run`**: Ejecuta la interfaz gráfica y el duelo de campeones.
- **`make train`**: Lanza el proceso de Grid Search y Algoritmo Genético.
- **`make tournament`**: Ejecuta el torneo de Elo entre los agentes guardados.
- **`make shell`**: Acceso directo al contenedor.
- **`make stop`**: Detiene y limpia los contenedores.

---

## 📂 Estructura del Proyecto

```text
/
├── compose.yml           # Configuración de Podman y X11
├── Dockerfile            # Imagen base (Python + dependencias SDL)
├── pyproject.toml        # Dependencias (Numpy, Pygame, etc.)
├── Makefile              # Atajos de ejecución
├── models/               # Almacenamiento de Q-Tables (.pkl)
└── src/
    ├── agent.py          # Clase QLearner y lógica de Bellman
    ├── minimax.py        # Agente perfecto para evaluación
    ├── genetic.py        # Lógica del Algoritmo Genético
    ├── dashboard.py      # Generación de gráficas de aprendizaje
    └── main.py           # Interfaz visual y ejecución principal
```

---

## 📊 Métricas de Evaluación

El éxito de los agentes se mide bajo tres criterios:
1.  **Punto de Perfección ($P_0$):** Número de partidas necesarias para dejar de perder contra Minimax.
2.  **Rating Elo:** Puntaje relativo de fuerza entre las distintas configuraciones de agentes.
3.  **Estabilidad de Convergencia:** Capacidad del agente para mantener el nivel óptimo tras alcanzarlo.

---

## 🔧 Solución de Problemas Comunes

### 1. Error de Display (Pygame)
Si al ejecutar `make run` obtienes un error de video, asegúrate de habilitar el acceso a X11 en el host:
```bash
xhost +local:
```

### 2. Sincronización de dependencias
Si notas que faltan librerías dentro del contenedor tras actualizar el `pyproject.toml`:
```bash
podman exec -it qlearning_dev uv sync
```

### 3. Persistencia de Modelos
Los modelos se guardan en la carpeta `models/`. Si deseas resetear el entrenamiento, vacía esta carpeta antes de ejecutar el proceso de entrenamiento.
```bash
rm models/*.pkl
```
5.  **Comandos:** Añadí `make train` y `make tournament` como sugerencia para separar el entrenamiento de la visualización.

¡Mucho éxito con este nuevo enfoque! Es un salto de calidad enorme respecto al Minimax tradicional.
