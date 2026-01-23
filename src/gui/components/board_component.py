import pygame

from src.config import CIRCLE_COLOR, CROSS_COLOR, LINE_COLOR, LINE_WIDTH
from src.gui.shapes import ShapeDrawer


class BoardComponent:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.rows = 3
        self.cols = 3

        self.cell_w = self.rect.width // self.cols
        self.cell_h = self.rect.height // self.rows

    def draw_grid(self, surface):
        pygame.draw.rect(surface, LINE_COLOR, self.rect, 3)

        # Líneas verticales
        for i in range(1, self.cols):
            x = self.rect.left + i * self.cell_w
            pygame.draw.line(surface, LINE_COLOR, (x, self.rect.top), (x, self.rect.bottom), LINE_WIDTH)

        # Líneas horizontales
        for i in range(1, self.rows):
            y = self.rect.top + i * self.cell_h
            pygame.draw.line(surface, LINE_COLOR, (self.rect.left, y), (self.rect.right, y), LINE_WIDTH)

    def draw_symbols(self, surface, board_array, inverted):
        for r in range(self.rows):
            for c in range(self.cols):
                val = board_array[r][c]
                if val == 0:
                    continue

                cell_rect = pygame.Rect(
                    self.rect.left + c * self.cell_w, self.rect.top + r * self.cell_h, self.cell_w, self.cell_h
                )

                color = CROSS_COLOR if val == 1 else CIRCLE_COLOR
                is_x = (val == 1 and not inverted) or (val == 2 and inverted)
                color = CROSS_COLOR if is_x else CIRCLE_COLOR
                if is_x:
                    ShapeDrawer.draw_x(surface, cell_rect, color)
                else:
                    ShapeDrawer.draw_o(surface, cell_rect, color)

    def get_cell_from_mouse(self, mouse_pos):
        if not self.rect.collidepoint(mouse_pos):
            return None

        local_x = mouse_pos[0] - self.rect.left
        local_y = mouse_pos[1] - self.rect.top

        row = local_y // self.cell_h
        col = local_x // self.cell_w

        row = max(0, min(int(row), self.rows - 1))
        col = max(0, min(int(col), self.cols - 1))

        return row, col

    def draw_ghost(self, surface, row, col, turn, inverted):
        """Dibuja el símbolo traslúcido en la celda donde está el mouse."""
        cell_rect = pygame.Rect(
            self.rect.left + col * self.cell_w, self.rect.top + row * self.cell_h, self.cell_w, self.cell_h
        )

        ghost_surf = pygame.Surface((self.cell_w, self.cell_h), pygame.SRCALPHA)
        local_rect = pygame.Rect(0, 0, self.cell_w, self.cell_h)

        is_x = (turn == 1 and not inverted) or (turn == 2 and inverted)
        color = (*CROSS_COLOR, 100) if is_x else (*CIRCLE_COLOR, 100)

        if is_x:
            ShapeDrawer.draw_x(ghost_surf, local_rect, color)
        else:
            ShapeDrawer.draw_o(ghost_surf, local_rect, color)

        surface.blit(ghost_surf, cell_rect.topleft)
