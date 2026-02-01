import os
import pickle
import random

from src.benchmarks.utils import evaluate_vs_minimax
from src.game_logic.board import Board

# Definimos el intervalo de evaluación aquí, si es necesario, o lo pasamos como parámetro
EVAL_INTERVAL = 200


def train_with_decay(
    agent,
    episodes=20000,
    minimax_ratio=0.3,
    pickle_path="tictactoe_lookup.pkl",
    epsilon_decay_gen=None,
    reward_draw_gen=0.5,
    start_epsilon=1.0,
    progress_callback=None,
    # --- NUEVO PARÁMETRO ---
    record_curve=False,
):
    if not os.path.exists(pickle_path):
        lookup_table = None
    else:
        with open(pickle_path, "rb") as f:
            lookup_table = pickle.load(f)

    board = Board()
    agent.epsilon = start_epsilon
    episodes_to_optimal = episodes

    if epsilon_decay_gen is None:
        decay_factor = start_epsilon / episodes
    else:
        decay_factor = epsilon_decay_gen

    # --- NUEVA LISTA PARA REGISTRAR LA CURVA ---
    learning_curve_data = []

    for episode in range(episodes):
        if progress_callback:
            progress_callback(episode, episodes)

        board.reset()
        agent.epsilon = max(0.01, agent.epsilon - decay_factor)

        r = random.random()
        if r < minimax_ratio / 2:
            mode = 1
        elif r < minimax_ratio:
            mode = 2
        else:
            mode = 0

        history = {1: None, 2: None}

        while not board.game_over:
            current_player = board.turn
            state_key = agent.get_state_key(board.board)

            # DETERMINAR QUIÉN MUEVE
            is_master_turn = (current_player == 2 and mode == 1) or (current_player == 1 and mode == 2)

            if is_master_turn:
                state_hash = tuple(item for row in board.board for item in row)
                move_data = lookup_table.get(state_hash) if lookup_table else None
                action = move_data["move"] if isinstance(move_data, dict) else move_data
                if action is None:
                    action = random.choice(board.get_available_moves())
            else:
                action = agent.choose_action(board)
            if not is_master_turn:
                history[current_player] = (state_key, action)

            board.make_move(action[0], action[1])

            # APRENDIZAJE DURANTE EL JUEGO (TD Learning)
            other_player = 2 if current_player == 1 else 1
            if history[other_player]:
                prev_state, prev_action = history[other_player]
                if not board.game_over:
                    current_board_state = agent.get_state_key(board.board)
                    agent.learn(prev_state, prev_action, 0, current_board_state, board.get_available_moves(), False)
                else:
                    if board.winner == other_player:
                        reward = 1
                    elif board.winner == 0 or board.winner is None:
                        reward = reward_draw_gen
                    else:
                        reward = -1

                    agent.learn(prev_state, prev_action, reward, None, [], True)

        if board.game_over:
            last_player = 1 if board.turn == 2 else 2
            is_last_player_master = (last_player == 2 and mode == 1) or (last_player == 1 and mode == 2)

            if not is_last_player_master and history[last_player]:
                s, a = history[last_player]
                if board.winner == last_player:
                    agent.learn(s, a, 1, None, [], True)
                elif board.winner == 0 or board.winner is None:
                    agent.learn(s, a, reward_draw_gen, None, [], True)
                else:
                    agent.learn(s, a, -1, None, [], True)

        # --- REGISTRO DE PUNTOS INTERMEDIOS Y CONDICIÓN DE BREAK ---
        # Si se solicita la curva O si es un punto de chequeo
        if record_curve and (episode > 0 and episode % EVAL_INTERVAL == 0):
            # Usar un número menor de juegos para la curva para ser más rápido
            wins_c, losses_c, draws_c = evaluate_vs_minimax(agent, num_games=20)
            success_rate = (wins_c + draws_c) / 20.0

            learning_curve_data.append({"episode": episode, "success_rate": success_rate})

        # Condición de break (sigue siendo cada 200)
        if episode % 200 == 0 and episode > 1000:
            n_test = 100
            wins, losses, draws = evaluate_vs_minimax(agent, num_games=n_test)

            if losses == 0:
                episodes_to_optimal = episode
                break

    # Asegurar que se registra el punto final si el entrenamiento no fue roto por el break
    if record_curve and episodes_to_optimal == episodes and episodes % EVAL_INTERVAL != 0:
        wins_c, losses_c, draws_c = evaluate_vs_minimax(agent, num_games=20)
        success_rate = (wins_c + draws_c) / 20.0
        learning_curve_data.append({"episode": episodes, "success_rate": success_rate})

    agent.epsilon = 0.01
    return agent, episodes_to_optimal, learning_curve_data
