import pygame

from src.config import FONT_COLOR, FONT_SIZE, MENU_SELECTED_COLOR


class MenuComponent:
    def __init__(self, screen_rect, font, title_font):
        self.rect = screen_rect
        self.font = font
        self.title_font = title_font

    def draw(self, surface, options, selected_option):
        option_rects = []
        title_surf = self.title_font.render("Tres en Raya", True, FONT_COLOR)
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.height // 4))
        surface.blit(title_surf, title_rect)

        # Dibujar Opciones
        for i, option in enumerate(options):
            y = self.rect.centery + i * (FONT_SIZE + 35)
            is_sel = i == selected_option

            text_str = f">  {option}  <" if is_sel else option
            color = MENU_SELECTED_COLOR if is_sel else (180, 180, 180)

            txt_surf = self.font.render(text_str, True, color)
            txt_rect = txt_surf.get_rect(center=(self.rect.centerx, y))

            if is_sel:
                bg = txt_rect.inflate(40, 15)
                pygame.draw.rect(surface, (68, 71, 90), bg, border_radius=15)
                pygame.draw.rect(surface, MENU_SELECTED_COLOR, bg, 2, border_radius=15)

            surface.blit(txt_surf, txt_rect)
            option_rects.append(txt_rect.inflate(40, 20))

        return option_rects
