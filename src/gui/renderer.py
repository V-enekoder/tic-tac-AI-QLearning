import math
from typing import List

import pygame

from src.config import *


class Renderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen: pygame.Surface = screen
        self.font: pygame.font.Font = pygame.font.Font(None, 45)
        self.menu_font: pygame.font.Font = pygame.font.Font(None, MENU_FONT_SIZE)

        # Offsets Dinámicos
        self.board_offset_x = BOARD_OFFSET_X
        self.board_offset_y = BOARD_OFFSET_Y

        self.inverted_symbols = False

    def set_inverted(self, inverted: bool):
        """Si es True, Jugador 1 dibuja O (Círculo) y Jugador 2 dibuja X (Cruz)."""
        self.inverted_symbols = inverted

    def set_centered(self, is_centered: bool):
        """Alternar entre tablero centrado (H vs H) y alineado a la izquierda."""
        if is_centered:
            self.board_offset_x = (WIDTH - BOARD_WIDTH) // 2
        else:
            self.board_offset_x = BOARD_OFFSET_X

    def draw_menu(self, options: List[str], selected_option: int) -> List[pygame.Rect]:
        self.screen.fill(BG_COLOR)

        option_rects = []

        # Título con sombra
        title_font = pygame.font.Font(None, 80)
        title_text = title_font.render("Tres en Raya", True, (0, 0, 0))  # Sombra negra
        title_rect = title_text.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 4 + 4))
        self.screen.blit(title_text, title_rect)

        title_text_main = title_font.render("Tres en Raya", True, FONT_COLOR)
        title_rect_main = title_text_main.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        self.screen.blit(title_text_main, title_rect_main)

        # Opciones del menú
        for i, option in enumerate(options):
            center_x = WIDTH // 2
            center_y = HEIGHT // 2 + i * (FONT_SIZE + 35)

            # Texto base
            if i == selected_option:
                color = MENU_SELECTED_COLOR
                text_content = f">  {option}  <"
            else:
                color = (180, 180, 180)
                text_content = option

            text = self.font.render(text_content, True, color)
            rect = text.get_rect(center=(center_x, center_y))

            if i == selected_option:
                bg_rect = rect.inflate(40, 15)
                pygame.draw.rect(self.screen, (68, 71, 90), bg_rect, border_radius=15)
                pygame.draw.rect(
                    self.screen, MENU_SELECTED_COLOR, bg_rect, 2, border_radius=15
                )

            self.screen.blit(text, rect)

            # Guardar el rectángulo de colisión (un poco más grande para facilitar el clic)
            hitbox = rect.inflate(40, 20)
            option_rects.append(hitbox)

        return option_rects

    def draw_turn_indicator(self, turn: int, player_type: str):
        """Dibuja quién está jugando en la parte superior."""

        is_x = (turn == 1 and not self.inverted_symbols) or (
            turn == 2 and self.inverted_symbols
        )
        symbol_str = "X" if is_x else "O"

        # Color based on symbol
        color_rgb = CROSS_COLOR if is_x else CIRCLE_COLOR

        if player_type == "HUMAN":
            text_str = f"Turno del Humano ({symbol_str})"
        else:
            text_str = f"Turno de la IA ({symbol_str})"

        text = self.font.render(text_str, True, color_rgb)
        center_x = self.board_offset_x + BOARD_WIDTH // 2
        text_rect = text.get_rect(center=(center_x, BOARD_OFFSET_Y // 2))
        self.screen.blit(text, text_rect)

    def draw_ghost_symbol(self, row, col, turn):
        """Dibuja un símbolo semitransparente (hover)."""
        center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_offset_x
        center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_Y

        # Crear superficie temporal con transparencia
        ghost_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

        alpha = 100

        if turn == 1:
            if self.inverted_symbols:
                color = (*CIRCLE_COLOR, alpha)
                radius = CIRCLE_RADIUS
                center = (SQUARE_SIZE // 2, SQUARE_SIZE // 2)
                pygame.draw.circle(ghost_surf, color, center, radius, CIRCLE_WIDTH)
            else:
                margin = SQUARE_SIZE // 4
                color = (*CROSS_COLOR, alpha)
                start_desc = (margin, margin)
                end_desc = (SQUARE_SIZE - margin, SQUARE_SIZE - margin)
                start_asc = (margin, SQUARE_SIZE - margin)
                end_asc = (SQUARE_SIZE - margin, margin)
                pygame.draw.line(ghost_surf, color, start_desc, end_desc, CROSS_WIDTH)
                pygame.draw.line(ghost_surf, color, start_asc, end_asc, CROSS_WIDTH)

        else:
            if self.inverted_symbols:
                margin = SQUARE_SIZE // 4
                color = (*CROSS_COLOR, alpha)
                start_desc = (margin, margin)
                end_desc = (SQUARE_SIZE - margin, SQUARE_SIZE - margin)
                start_asc = (margin, SQUARE_SIZE - margin)
                end_asc = (SQUARE_SIZE - margin, margin)
                pygame.draw.line(ghost_surf, color, start_desc, end_desc, CROSS_WIDTH)
                pygame.draw.line(ghost_surf, color, start_asc, end_asc, CROSS_WIDTH)
            else:
                color = (*CIRCLE_COLOR, alpha)
                radius = CIRCLE_RADIUS
                center = (SQUARE_SIZE // 2, SQUARE_SIZE // 2)
                pygame.draw.circle(ghost_surf, color, center, radius, CIRCLE_WIDTH)

        self.screen.blit(
            ghost_surf,
            (
                col * SQUARE_SIZE + self.board_offset_x,
                row * SQUARE_SIZE + BOARD_OFFSET_Y,
            ),
        )

    def draw_grid(self):
        """Dibuja las líneas del tablero y el borde completo."""
        self.screen.fill(BG_COLOR)

        board_height = BOARD_ROWS * SQUARE_SIZE
        pygame.draw.rect(
            self.screen,
            SQUARE_HOVER_COLOR,
            (self.board_offset_x, BOARD_OFFSET_Y, BOARD_WIDTH, board_height),
            3,
        )

        # Líneas horizontales
        for i in range(1, BOARD_ROWS):
            y = i * SQUARE_SIZE + BOARD_OFFSET_Y
            pygame.draw.line(
                self.screen,
                LINE_COLOR,
                (self.board_offset_x, y),
                (BOARD_WIDTH + self.board_offset_x, y),
                LINE_WIDTH,
            )
        # Líneas verticales
        for i in range(1, BOARD_COLS):
            x = i * SQUARE_SIZE + self.board_offset_x
            pygame.draw.line(
                self.screen,
                LINE_COLOR,
                (x, BOARD_OFFSET_Y),
                (x, board_height + BOARD_OFFSET_Y),
                LINE_WIDTH,
            )

    def draw_symbols(self, board_array):
        """Dibuja las X y O en el tablero."""
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_offset_x
                center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_Y

                is_p1 = board_array[row][col] == 1
                is_p2 = board_array[row][col] == 2

                draw_x = (is_p1 and not self.inverted_symbols) or (
                    is_p2 and self.inverted_symbols
                )
                draw_o = (is_p2 and not self.inverted_symbols) or (
                    is_p1 and self.inverted_symbols
                )

                if draw_x:
                    margin = SQUARE_SIZE // 4
                    start_desc = (center_x - margin, center_y - margin)
                    end_desc = (center_x + margin, center_y + margin)
                    start_asc = (center_x - margin, center_y + margin)
                    end_asc = (center_x + margin, center_y - margin)
                    pygame.draw.line(
                        self.screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH
                    )
                    pygame.draw.line(
                        self.screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH
                    )
                elif draw_o:
                    pygame.draw.circle(
                        self.screen,
                        CIRCLE_COLOR,
                        (center_x, center_y),
                        CIRCLE_RADIUS,
                        CIRCLE_WIDTH,
                    )

    def draw_win_line(self, board):
        if not board.win_info:
            return

        win_type, index = board.win_info

        if win_type == "row":
            y_pos = index * SQUARE_SIZE + SQUARE_SIZE // 2 + BOARD_OFFSET_Y
            start_pos = (15 + self.board_offset_x, y_pos)
            end_pos = (BOARD_WIDTH - 15 + self.board_offset_x, y_pos)
        elif win_type == "col":
            x_pos = index * SQUARE_SIZE + SQUARE_SIZE // 2 + self.board_offset_x
            start_pos = (x_pos, 15 + BOARD_OFFSET_Y)
            end_pos = (x_pos, (BOARD_ROWS * SQUARE_SIZE) - 15 + BOARD_OFFSET_Y)
        elif win_type == "diag":
            if index == 1:  # Descendente
                start_pos = (15 + self.board_offset_x, 15 + BOARD_OFFSET_Y)
                end_pos = (
                    BOARD_WIDTH - 15 + self.board_offset_x,
                    (BOARD_ROWS * SQUARE_SIZE) - 15 + BOARD_OFFSET_Y,
                )
            else:  # Ascendente
                start_pos = (
                    15 + self.board_offset_x,
                    (BOARD_ROWS * SQUARE_SIZE) - 15 + BOARD_OFFSET_Y,
                )
                end_pos = (BOARD_WIDTH - 15 + self.board_offset_x, 15 + BOARD_OFFSET_Y)

        # Efecto Neon Glow
        # Dibujamos varias líneas con distinta transparencia y grosor
        glow_colors = [
            (*WIN_LINE_COLOR, 50),
            (*WIN_LINE_COLOR, 100),
            (*WIN_LINE_COLOR, 255),
        ]
        widths = [LINE_WIDTH + 15, LINE_WIDTH + 5, LINE_WIDTH]

        glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        for i in range(3):
            pygame.draw.line(glow_surf, glow_colors[i], start_pos, end_pos, widths[i])

        self.screen.blit(glow_surf, (0, 0))

    def draw_game_over_text(self, board):
        if not board.game_over:
            return

        if board.winner == 0:
            text = "¡Es un empate!"
        else:
            text = f"¡Jugador {board.winner} gana!"

        rendered_text = self.font.render(text, True, FONT_COLOR)
        text_rect = rendered_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))

        restart_text = self.font.render("Pulsa 'R' para reiniciar", True, FONT_COLOR)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        # Fondo semi-transparente para el texto
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        self.screen.blit(rendered_text, text_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw_mini_board(self, x, y, size, board_state):
        """Dibuja un mini tablero en la posición (x, y)."""
        # Fondo del mini tablero
        rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(self.screen, (255, 255, 255), rect)
        pygame.draw.rect(self.screen, LINE_COLOR, rect, 2)

        cell_size = size // 3

        # Líneas
        for i in range(1, 3):
            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                (x, y + i * cell_size),
                (x + size, y + i * cell_size),
                1,
            )
            pygame.draw.line(
                self.screen,
                (0, 0, 0),
                (x + i * cell_size, y),
                (x + i * cell_size, y + size),
                1,
            )

        # Símbolos
        font_mini = pygame.font.Font(None, int(cell_size * 1.5))
        for r in range(3):
            for c in range(3):
                val = board_state[r][c]
                if val != 0:
                    symbol = "X" if val == 1 else "O"
                    color = (0, 0, 0)
                    text = font_mini.render(symbol, True, color)
                    text_rect = text.get_rect(
                        center=(
                            x + c * cell_size + cell_size // 2,
                            y + r * cell_size + cell_size // 2,
                        )
                    )
                    self.screen.blit(text, text_rect)

    def draw_decision_graph(self, root_node):
        if not root_node:
            return

        board_end_x = self.board_offset_x + BOARD_WIDTH
        screen_width = self.screen.get_width()
        available_width = screen_width - board_end_x

        panel_center_x = board_end_x + (available_width // 2)

        start_y = 30

        self.draw_mini_board(
            panel_center_x - 15, start_y, 30, root_node["board_matrix"]
        )

        self._draw_cascade_level(root_node, panel_center_x, start_y + 40)

    def _draw_cascade_level(self, parent_node, parent_x, y):
        children = parent_node.get("children", [])
        if not children:
            return

        count = len(children)

        mini_size = 24

        if count >= 5:
            gap = 28
        else:
            gap = 40

        chosen_index = -1
        for i, child in enumerate(children):
            if child.get("children") or child.get("is_chosen"):
                chosen_index = i
                break

        if chosen_index != -1:
            start_x = parent_x - (chosen_index * gap)
        else:
            total_row_width = (count - 1) * gap
            start_x = parent_x - (total_row_width / 2)

        chosen_child = None
        chosen_child_x = 0

        for i, child in enumerate(children):
            current_x = start_x + (i * gap)

            score = child["score"]
            if score > 0:
                color = (0, 255, 0)  # Verde
            elif score < 0:
                color = (255, 0, 0)  # Rojo
            else:
                color = (150, 150, 150)  # Gris

            is_chosen = i == chosen_index

            line_width = 3 if is_chosen else 1
            line_color = (255, 255, 0) if is_chosen else (60, 60, 60)

            # Dibujar línea al padre
            pygame.draw.line(
                self.screen,
                line_color,
                (parent_x, y - 10),
                (current_x, y + 10),
                line_width,
            )

            self.draw_mini_board(
                current_x - (mini_size // 2), y + 10, mini_size, child["board_matrix"]
            )

            if is_chosen:
                rect = pygame.Rect(
                    current_x - (mini_size // 2) - 2,
                    y + 10 - 2,
                    mini_size + 4,
                    mini_size + 4,
                )
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 2)
            else:
                rect = pygame.Rect(
                    current_x - (mini_size // 2) - 1,
                    y + 10 - 1,
                    mini_size + 2,
                    mini_size + 2,
                )
                pygame.draw.rect(self.screen, color, rect, 1)

            if is_chosen or count < 6:
                font = pygame.font.Font(None, 16)
                score_txt = font.render(
                    str(score), True, (255, 255, 255) if is_chosen else color
                )
                txt_rect = score_txt.get_rect(center=(current_x, y + mini_size + 15))
                self.screen.blit(score_txt, txt_rect)

            if is_chosen:
                chosen_child = child
                chosen_child_x = current_x

        if chosen_child:
            self._draw_cascade_level(chosen_child, chosen_child_x, y + 70)
