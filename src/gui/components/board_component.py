import pygame

from src.config import CIRCLE_COLOR, CROSS_COLOR, LINE_COLOR, LINE_WIDTH
from src.gui.shapes import ShapeDrawer


class BoardComponent:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect  # Esta es la "caja" donde vive el tablero
        self.rows = 3
        self.cols = 3

        # Calculamos el tamaño de celda dinámicamente según el tamaño del Rect
        self.cell_w = self.rect.width // self.cols
        self.cell_h = self.rect.height // self.rows

    def draw_grid(self, surface):
        # Dibujar el borde exterior usando el rect del componente
        pygame.draw.rect(surface, LINE_COLOR, self.rect, 3)

        # Líneas verticales
        for i in range(1, self.cols):
            # La x es: borde_izquierdo + (columna * ancho_celda)
            x = self.rect.left + i * self.cell_w
            pygame.draw.line(surface, LINE_COLOR, (x, self.rect.top), (x, self.rect.bottom), LINE_WIDTH)

        # Líneas horizontales
        for i in range(1, self.rows):
            # La y es: borde_superior + (fila * alto_celda)
            y = self.rect.top + i * self.cell_h
            pygame.draw.line(surface, LINE_COLOR, (self.rect.left, y), (self.rect.right, y), LINE_WIDTH)

    def draw_symbols(self, surface, board_array):
        for r in range(self.rows):
            for c in range(self.cols):
                val = board_array[r][c]
                if val == 0:
                    continue

                # Creamos un Rect para la celda actual
                cell_rect = pygame.Rect(
                    self.rect.left + c * self.cell_w, self.rect.top + r * self.cell_h, self.cell_w, self.cell_h
                )

                # Usamos nuestra utilidad ShapeDrawer (del paso anterior)
                color = CROSS_COLOR if val == 1 else CIRCLE_COLOR
                if val == 1:
                    ShapeDrawer.draw_x(surface, cell_rect, color)
                else:
                    ShapeDrawer.draw_o(surface, cell_rect, color)

    def get_cell_from_mouse(self, mouse_pos):
        # Si el clic está fuera del rect del tablero, ni lo procesamos
        if not self.rect.collidepoint(mouse_pos):
            return None

        # Restamos el offset para obtener coordenadas locales (0 a BOARD_WIDTH)
        local_x = mouse_pos[0] - self.rect.left
        local_y = mouse_pos[1] - self.rect.top

        row = local_y // self.cell_h
        col = local_x // self.cell_w
        return int(row), int(col)
