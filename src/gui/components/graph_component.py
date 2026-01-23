import pygame

from src.config import *
from src.gui.shapes import ShapeDrawer


class GraphComponent:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.font_small = pygame.font.Font(None, 18)
        self.font_title = pygame.font.Font(None, 36)
        self.font_legend = pygame.font.Font(None, 20)

    def draw(self, surface, root_node, inverted_symbols):
        pygame.draw.rect(surface, (30, 30, 40), self.rect)

        pygame.draw.line(surface, (100, 100, 150), self.rect.topleft, self.rect.bottomleft, 2)

        if not root_node:
            text = self.font_title.render("Esperando IA...", True, (100, 100, 100))
            surface.blit(text, text.get_rect(center=self.rect.center))
            return

        title_surf = self.font_title.render("Grafo Explorado", True, (255, 255, 255))
        surface.blit(title_surf, title_surf.get_rect(center=(self.rect.centerx, 30)))
        self._draw_legend(surface)

        depth = self._get_tree_depth(root_node)
        margin_top = 100
        available_height = self.rect.height - margin_top - 40
        vertical_step = max(60, min(available_height / (depth + 1), 140)) if depth > 0 else 100

        mini_size_root = 32
        root_x = self.rect.centerx
        root_y = margin_top

        self._draw_mini_board(
            surface, root_x - mini_size_root // 2, root_y, mini_size_root, root_node["board_matrix"], inverted_symbols
        )

        self._draw_cascade_level(surface, root_node, root_x, root_y + vertical_step, vertical_step, inverted_symbols)

    def _draw_mini_board(self, surface, x, y, size, board_state, inverted):
        rect = pygame.Rect(x, y, size, size)
        pygame.draw.rect(surface, (255, 255, 255), rect)
        pygame.draw.rect(surface, (0, 0, 0), rect, 1)
        cell_size = size // 3
        for i in range(1, 3):
            pygame.draw.line(surface, (200, 200, 200), (x, y + i * cell_size), (x + size, y + i * cell_size), 1)
            pygame.draw.line(surface, (200, 200, 200), (x + i * cell_size, y), (x + i * cell_size, y + size), 1)

        for r in range(3):
            for c in range(3):
                val = board_state[r][c]
                if val == 0:
                    continue

                cell_rect = pygame.Rect(x + c * cell_size, y + r * cell_size, cell_size, cell_size)
                is_x = (val == 1 and not inverted) or (val == 2 and inverted)

                if is_x:
                    ShapeDrawer.draw_x(surface, cell_rect, (0, 0, 0), width_weight=0.15)
                else:
                    ShapeDrawer.draw_o(surface, cell_rect, (0, 0, 0), width_weight=0.15)

    def _draw_cascade_level(self, surface, parent_node, parent_x, y, vertical_step, inverted):
        children = parent_node.get("children", [])
        if not children:
            return

        count = len(children)
        mini_size = 28
        gap = max(mini_size + 2, min(45, (self.rect.width - 40) / count))

        chosen_index = next((i for i, c in enumerate(children) if c.get("is_chosen")), -1)

        total_w = (count - 1) * gap
        start_x = parent_x - (chosen_index * gap if chosen_index != -1 else total_w / 2)

        start_x = max(self.rect.left + mini_size, min(start_x, self.rect.right - total_w - mini_size))

        chosen_child = None
        chosen_x = 0

        for i, child in enumerate(children):
            curr_x = start_x + (i * gap)
            is_chosen = i == chosen_index

            line_color = (255, 255, 0) if is_chosen else (80, 80, 90)
            start_line = (parent_x, y - vertical_step + mini_size)
            end_line = (curr_x, y - 5)
            pygame.draw.line(surface, line_color, start_line, end_line, 2 if is_chosen else 1)

            self._draw_mini_board(
                surface, curr_x - mini_size // 2, y - mini_size // 2, mini_size, child["board_matrix"], inverted
            )

            score = child["score"]
            color_score = (0, 255, 0) if score > 0 else (255, 0, 0) if score < 0 else (150, 150, 150)
            rect_border = pygame.Rect(curr_x - mini_size // 2 - 1, y - mini_size // 2 - 1, mini_size + 2, mini_size + 2)
            pygame.draw.rect(surface, (255, 255, 0) if is_chosen else color_score, rect_border, 2 if is_chosen else 1)

            score_txt = self.font_small.render(str(score), True, color_score)
            surface.blit(score_txt, score_txt.get_rect(center=(curr_x, y + mini_size // 2 + 10)))

            if is_chosen:
                chosen_child = child
                chosen_x = curr_x

        if chosen_child:
            self._draw_cascade_level(surface, chosen_child, chosen_x, y + vertical_step, vertical_step, inverted)

    def _draw_legend(self, surface):
        items = [("Ganar", (0, 255, 0)), ("Perder", (255, 0, 0)), ("Elegido", (255, 255, 0))]
        curr_x = self.rect.left + 20
        for text, color in items:
            pygame.draw.rect(surface, color, (curr_x, 60, 10, 10))
            txt = self.font_legend.render(text, True, (200, 200, 200))
            surface.blit(txt, (curr_x + 15, 58))
            curr_x += 80

    def _get_tree_depth(self, node):
        if not node or not node.get("children"):
            return 0
        chosen = next((c for c in node["children"] if c.get("is_chosen")), None)
        return 1 + self._get_tree_depth(chosen) if chosen else 1
