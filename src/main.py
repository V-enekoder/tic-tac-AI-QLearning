import os
import sys
from enum import Enum

import pygame

from src.ai.minimax import (
    find_best_move_and_viz,
)
from src.ai.ql_agent import QLearningAgent
from src.config import *
from src.game_logic.board import Board
from src.gui.renderer import Renderer
from src.training.gym import train_with_decay


# --- Enums y Constantes ---
class GameState(Enum):
    MENU = 0
    AI_SELECTION = 1
    PLAYING = 2
    CUSTOM_SETUP = 3


class GameController:
    def __init__(self):
        pygame.display.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Comparador de IA: Minimax vs Alfa-Beta")
        self.clock = pygame.time.Clock()

        self.board = Board()
        self.renderer = Renderer(self.screen)

        self.state = GameState.MENU
        self.running = True

        # Variables para controlar la pausa de análisis
        self.paused_for_analysis = False
        self.pause_start_time = 0
        self.pause_duration = 1000  # 1 segundo en milisegundos

        self.player_types = [PlayerType.HUMAN, PlayerType.HUMAN]
        self.ai_speed_selected = None
        self.last_graph_data = []
        self.waiting_for_step = False

        # Configuración de Menús
        self.menu_options = [
            "Humano vs Humano",
            "Humano vs QLearning",
            "Diseña tu propio agente",
        ]
        self.menu_selection = 0

        self.start_options = ["Humano Inicia", "IA Inicia"]
        self.start_selection = 0

        self.menu_rects = []

        self.q_agent = self._setup_q_agent()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def _setup_q_agent(self):
        agent = QLearningAgent(epsilon=0)
        model_path = "src/models/q_table.pkl"

        if os.path.exists(model_path):
            print("Cargando modelo Q-Learning existente...")
            agent.load_model(model_path)
        else:
            print("Entrenando nuevo agente Q-Learning (espera unos segundos)...")

            agent, _ = train_with_decay(QLearningAgent(), episodes=50000)
            agent.save_model(model_path)
            agent.epsilon = 0
        return agent

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.state == GameState.MENU:
                self._handle_menu_input(event, self.menu_options, is_main_menu=True)

            elif self.state == GameState.AI_SELECTION:
                self._handle_menu_input(event, self.start_options, is_main_menu=False)

            elif self.state == GameState.CUSTOM_SETUP:
                self._handle_custom_setup_input(event)

            elif self.state == GameState.PLAYING:
                self._handle_playing_input(event)

    def _handle_menu_input(self, event, options_list, is_main_menu):
        selection_attr = "menu_selection" if is_main_menu else "start_selection"
        current_selection = getattr(self, selection_attr)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                setattr(
                    self,
                    selection_attr,
                    (current_selection - 1) % len(options_list),
                )
            elif event.key == pygame.K_DOWN:
                setattr(
                    self,
                    selection_attr,
                    (current_selection + 1) % len(options_list),
                )
            elif event.key == pygame.K_RETURN:
                if is_main_menu:
                    self._confirm_main_menu_selection()
                else:
                    self._confirm_ai_selection()
            elif event.key == pygame.K_ESCAPE and not is_main_menu:
                self.state = GameState.MENU

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    setattr(self, selection_attr, i)
                    if is_main_menu:
                        self._confirm_main_menu_selection()
                    else:
                        self._confirm_ai_selection()
                    break

        mouse_pos = pygame.mouse.get_pos()
        for i, rect in enumerate(self.menu_rects):
            if rect.collidepoint(mouse_pos):
                setattr(self, selection_attr, i)

    def _confirm_main_menu_selection(self):
        sel = self.menu_selection
        if sel == 0:  # H v H
            self.start_game([PlayerType.HUMAN, PlayerType.HUMAN])
        elif sel == 1:  # Humano vs QLearning
            self.ai_speed_selected = PlayerType.AI_QL
            self.state = GameState.AI_SELECTION
        elif sel == 2:  # Diseña tu propio agente
            self.state = GameState.CUSTOM_SETUP

    def _confirm_ai_selection(self):
        p1 = PlayerType.HUMAN
        p2 = self.ai_speed_selected

        if self.start_selection == 0:
            self.start_game([p1, p2])
        else:
            self.start_game([p2, p1])

    def _handle_custom_setup_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU
            return

        params = self.renderer.config_view.handle_event(event)
        if params:
            self._start_custom_game(params)

    def _start_custom_game(self, params):
        print(f"Entrenando agente personalizado con: {params}")

        # Función callback para actualizar la barra de progreso
        def progress_hook(current, total):
            # Procesar eventos para mantener la ventana viva (evita que Windows diga "no responde")
            pygame.event.pump()
            self.renderer.draw_training_progress(current, total)

        new_agent = QLearningAgent(alpha=params["alpha"], gamma=params["gamma"], epsilon=params["epsilon"])

        # Entrenar con el hook
        self.q_agent, _ = train_with_decay(
            new_agent, episodes=params["episodes"], start_epsilon=params["epsilon"], progress_callback=progress_hook
        )

        # Ir a selección de turno
        self.ai_speed_selected = PlayerType.AI_QL
        self.state = GameState.AI_SELECTION

    def _handle_playing_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset_board()
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
            elif event.key == pygame.K_RETURN and self.waiting_for_step:
                self.waiting_for_step = False

        if event.type == pygame.MOUSEBUTTONDOWN and not self.board.game_over:
            current_player = self.player_types[self.board.turn - 1]
            if current_player == PlayerType.HUMAN:
                self._process_human_click(event.pos)

    def _process_human_click(self, pos):
        # El componente tablero ahora sabe traducir la posición del mouse
        move = self.renderer.get_cell_from_mouse(pos)

        if move:
            row, col = move
            if self.board.is_valid_move(row, col):
                self.board.make_move(row, col)

    def update(self):
        if self.state == GameState.PLAYING:
            self._update_game_logic()

    def _update_game_logic(self):
        if self.waiting_for_step:
            return

        # Verificar si estamos en pausa para análisis
        if self.paused_for_analysis:
            current_time = pygame.time.get_ticks()
            if current_time - self.pause_start_time >= self.pause_duration:
                self.paused_for_analysis = False
                # Ahora ejecutamos el turno de la IA
                self._execute_ai_turn_after_pause()
            return

        current_player = self.player_types[self.board.turn - 1]

        # Verificar si el jugador anterior era humano y ahora es QL para iniciar pausa
        if not self.board.game_over:
            previous_player_idx = (self.board.turn - 2) % 2  # Turno anterior
            if (
                self.player_types[previous_player_idx] == PlayerType.HUMAN
                and current_player == PlayerType.AI_QL
                and not self.board.game_over
            ):
                # Iniciar pausa para mostrar análisis
                self.paused_for_analysis = True
                self.pause_start_time = pygame.time.get_ticks()
                return

        if not self.board.game_over and current_player in [
            PlayerType.AI_SLOW,
            PlayerType.AI_FAST,
            PlayerType.AI_QL,
        ]:
            self._execute_ai_turn(current_player)

    def _execute_ai_turn_after_pause(self):
        """Ejecuta el turno de la IA después de la pausa de análisis."""
        current_player = self.player_types[self.board.turn - 1]
        if current_player == PlayerType.AI_QL:
            self._execute_ai_turn(current_player)

    def _execute_ai_turn(self, ai_type):
        self.draw()  # Dibujar antes para mostrar el estado actual

        # Añadir una pequeña pausa incluso después del análisis para que se vea el movimiento
        if ai_type == PlayerType.AI_QL:
            pygame.time.delay(500)  # 0.5 segundos adicionales para ver el análisis

        if ai_type == PlayerType.AI_QL:
            move = self.q_agent.choose_action(self.board)
            self.last_graph_data = []
        else:
            use_alpha_beta = ai_type == PlayerType.AI_FAST
            move, tree_data = find_best_move_and_viz(self.board, use_alpha_beta=use_alpha_beta)
            self.last_graph_data = tree_data

        if move:
            self.board.make_move(move[0], move[1])

            is_p1_ai = self.player_types[0] in [
                PlayerType.AI_SLOW,
                PlayerType.AI_FAST,
            ]
            is_p2_ai = self.player_types[1] in [
                PlayerType.AI_SLOW,
                PlayerType.AI_FAST,
            ]

            if is_p1_ai and is_p2_ai:
                self.waiting_for_step = True

    def draw(self):
        if self.state == GameState.MENU:
            self.menu_rects = self.renderer.draw_menu(self.menu_options, self.menu_selection)

        elif self.state == GameState.AI_SELECTION:
            self.menu_rects = self.renderer.draw_menu(self.start_options, self.start_selection)

        elif self.state == GameState.CUSTOM_SETUP:
            self.renderer.draw_custom_setup()

        elif self.state == GameState.PLAYING:
            self._draw_game_screen()

        pygame.display.update()

    def _draw_game_screen(self):
        is_h_vs_h = self.player_types == [PlayerType.HUMAN, PlayerType.HUMAN]
        self.renderer.set_centered(is_h_vs_h)

        should_invert = self.player_types[1] == PlayerType.HUMAN and self.player_types[0] != PlayerType.HUMAN
        self.renderer.set_inverted(should_invert)

        q_data = None
        # Si es turno de IA QL o Humano vs QL, mostrar "pensamientos" (valores Q)
        if PlayerType.AI_QL in self.player_types and not self.board.game_over:
            # Obtener valores Q para el estado actual
            # 1. Convertir tablero a tupla (como hace el ql_agent)
            state_key = tuple(tuple(row) for row in self.board.board)

            q_data = {}
            # 2. Iterar por todas las celdas (acciones posibles)
            for r in range(3):
                for c in range(3):
                    # La llave en q_table es (state_tuple, action_tuple)
                    full_key = (state_key, (r, c))
                    if full_key in self.q_agent.q_table:
                        q_data[(r, c)] = self.q_agent.q_table[full_key]

        # Determinar texto del encabezado de turno
        current_player_idx = self.board.turn - 1
        current_player_type = self.player_types[current_player_idx]

        # Determinar texto del encabezado
        if self.board.game_over:
            header_text = ""
            header_color = None
        elif current_player_type == PlayerType.HUMAN:
            # Si es Humano vs Humano, mostrar HUMANO 1 o HUMANO 2
            if is_h_vs_h:
                player_num = current_player_idx + 1  # 1 o 2
                header_text = f"TURNO: HUMANO {player_num}"
            else:
                header_text = "TURNO: HUMANO"
            header_color = (50, 150, 255)  # Azul
        elif current_player_type == PlayerType.AI_QL:
            header_text = "TURNO: AGENTE Q-LEARNING"
            header_color = (255, 100, 50)  # Naranja
        else:
            header_text = "TURNO"
            header_color = (200, 200, 200)  # Gris

        # Dibujar el juego
        self.renderer.draw_game(
            board=self.board, player_types=self.player_types, ai_tree=self.last_graph_data, q_values=q_data
        )

        # Dibujar encabezado de turno ENCIMA de todo (después del renderer)
        if header_text and not self.board.game_over:
            self._draw_turn_header(header_text, header_color)

        # Si estamos en pausa para análisis, mostrar indicador visual
        if self.paused_for_analysis:
            self._draw_analysis_indicator()

        current_player = self.player_types[self.board.turn - 1]
        if not self.board.game_over and current_player == PlayerType.HUMAN:
            self._draw_ghost_symbol()

        if self.waiting_for_step:
            self.renderer.draw_step_prompt()

    def _draw_turn_header(self, text, color):
        """Dibuja un encabezado prominente que indica de quién es el turno."""
        font_large = pygame.font.Font(None, 60)

        # Fondo del encabezado
        header_height = 70
        header_rect = pygame.Rect(0, 0, WIDTH, header_height)
        pygame.draw.rect(self.screen, (30, 30, 40), header_rect)
        pygame.draw.line(self.screen, color, (0, header_height - 2), (WIDTH, header_height - 2), 4)

        # Texto principal
        text_surface = font_large.render(text, True, color)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, header_height // 2))
        self.screen.blit(text_surface, text_rect)

    def _draw_analysis_indicator(self):
        """Muestra un mensaje indicando que la IA está analizando."""
        font = pygame.font.Font(None, 36)

        # Crear un semi-transparente overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # Negro semi-transparente
        self.screen.blit(overlay, (0, 0))

        # Texto principal
        text = font.render("Analizando jugada...", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)

        # Texto secundario
        subtext = pygame.font.Font(None, 24).render(
            "El agente Q-Learning está evaluando el tablero", True, (200, 200, 200)
        )
        subtext_rect = subtext.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        self.screen.blit(subtext, subtext_rect)

        # Indicador de progreso (animación simple)
        elapsed = pygame.time.get_ticks() - self.pause_start_time
        progress = min(elapsed / self.pause_duration, 1.0)

        bar_width = 200
        bar_height = 10
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = HEIGHT // 2 + 70

        # Fondo de la barra
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # Barra de progreso
        pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, int(bar_width * progress), bar_height))

    def _draw_ghost_symbol(self):
        mouse_pos = pygame.mouse.get_pos()
        move = self.renderer.get_cell_from_mouse(mouse_pos)

        if move is not None:
            row, col = move
            if self.board.is_valid_move(row, col):
                self.renderer.draw_ghost_symbol(row, col, self.board.turn)

    def start_game(self, players):
        self.player_types = players
        self.state = GameState.PLAYING
        self.reset_board()

    def reset_board(self):
        self.board = Board()
        self.last_graph_data = []
        self.waiting_for_step = False
        self.paused_for_analysis = False  # Reiniciar estado de pausa
        pygame.event.clear()


if __name__ == "__main__":
    game = GameController()
    game.run()
