import os

from src.ai.minimax import find_best_move_and_viz
from src.ai.qlearning import QLearningAgent
from src.game_logic.board import Board


def evaluate_vs_minimax(ql_agent: QLearningAgent, num_games=20) -> tuple:
    """
    Evalúa el rendimiento de un agente Q-Learning contra un agente Minimax perfecto.
    El Q-Agent debe estar en modo explotación (epsilon bajo).

    Retorna: (wins, losses, draws) del Q-Agent
    """

    ql_agent.epsilon = 0.01

    wins, losses, draws = 0, 0, 0

    for i in range(num_games):
        board = Board()

        ql_is_p1 = i % 2 == 0

        while not board.game_over:
            current_player = board.turn

            is_ql_turn = (current_player == 1 and ql_is_p1) or (current_player == 2 and not ql_is_p1)

            if is_ql_turn:
                move = ql_agent.choose_action(board)
            else:
                move, _ = find_best_move_and_viz(board, use_alpha_beta=True)

            if move:
                board.make_move(move[0], move[1])

        if board.winner == 0:
            draws += 1
        elif (board.winner == 1 and ql_is_p1) or (board.winner == 2 and not ql_is_p1):
            wins += 1
        else:
            losses += 1

    return wins, losses, draws
