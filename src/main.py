import sys

import numpy as np
import pygame

# --- CONSTANTES ---
WIDTH, HEIGHT = 600, 600
LINE_WIDTH = 15
BOARD_ROWS = 3
BOARD_COLS = 3
# Colores (R, G, B)
BG_COLOR = (28, 170, 156)  # Verde azulado (tipo pizarra)
LINE_COLOR = (23, 145, 135)  # Líneas un poco más oscuras
CIRCLE_COLOR = (239, 231, 200)  # Crema para el O
CROSS_COLOR = (66, 66, 66)  # Gris oscuro para la X


# Inicializar pantalla
def main():
    print("--- INICIANDO PRUEBA DE ENTORNO ---")
    print(f"Versión de Numpy detectada: {np.__version__}")

    # 1. Inicializar Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tres en Raya - Prueba de Entorno")
    screen.fill(BG_COLOR)

    # 2. Dibujar el Tablero (Líneas)
    # Líneas Horizontales
    pygame.draw.line(
        screen, LINE_COLOR, (0, HEIGHT // 3), (WIDTH, HEIGHT // 3), LINE_WIDTH
    )
    pygame.draw.line(
        screen, LINE_COLOR, (0, 2 * HEIGHT // 3), (WIDTH, 2 * HEIGHT // 3), LINE_WIDTH
    )
    # Líneas Verticales
    pygame.draw.line(
        screen, LINE_COLOR, (WIDTH // 3, 0), (WIDTH // 3, HEIGHT), LINE_WIDTH
    )
    pygame.draw.line(
        screen, LINE_COLOR, (2 * WIDTH // 3, 0), (2 * WIDTH // 3, HEIGHT), LINE_WIDTH
    )

    print("Ventana creada. Deberías ver el tablero.")

    # 3. Loop Principal del Juego
    running = True
    while running:
        for event in pygame.event.get():
            # Evento cerrar ventana (X)
            if event.type == pygame.QUIT:
                running = False
                print("Evento QUIT recibido. Cerrando...")

            # Evento clic del mouse (Prueba de interacción)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX = event.pos[0]  # Coordenada X
                mouseY = event.pos[1]  # Coordenada Y

                # Convertir pixel a fila/columna
                clicked_row = int(mouseY // (HEIGHT / 3))
                clicked_col = int(mouseX // (WIDTH / 3))

                print(f"Clic detectado en: Fila {clicked_row}, Columna {clicked_col}")

        # Actualizar la pantalla
        pygame.display.update()

    # Salir limpiamente
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
