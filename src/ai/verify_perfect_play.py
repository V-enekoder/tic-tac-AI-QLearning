import math
import os
import pickle

from src.ai.minimax import find_best_move_alpha_beta
from src.game_logic.board import Board


# --- Utilidades ---
def get_board_hash(board_matrix):
    return tuple(item for row in board_matrix for item in row)


class TableAI:
    def __init__(self, pickle_path="tictactoe_lookup.pkl"):
        with open(pickle_path, "rb") as f:
            self.table = pickle.load(f)

    def get_move(self, board):
        state_hash = get_board_hash(board.board)
        res = self.table.get(state_hash)
        # Manejar si guardaste el dict como {'move': ..., 'score': ...} o solo el movimiento
        if isinstance(res, dict):
            return res["move"]
        return res


# --- Simulador de Partida ---
def simulate_game(player1_type, player2_type, table_ai):
    """
    player_type puede ser 'table' o 'minimax'
    """
    board = Board()
    # Mapeo de turnos: Jugador 1 empieza, Jugador 2 sigue
    players = {1: player1_type, 2: player2_type}

    move_count = 0
    while not board.game_over:
        current_role = players[board.turn]

        if current_role == "table":
            move = table_ai.get_move(board)
        else:
            # Usamos tu función minimax alpha beta original
            move, _ = find_best_move_alpha_beta(board)

        if move is None:
            break

        board.make_move(move[0], move[1])
        move_count += 1

    return board.winner, move_count


# --- Script Principal ---
def main():
    pickle_path = "tictactoe_lookup.pkl"
    if not os.path.exists(pickle_path):
        print(f"Error: No se encuentra {pickle_path}. Genéralo primero.")
        return

    table_ai = TableAI(pickle_path)

    print("Iniciando pruebas de perfección...")
    print("-" * 40)

    # Prueba 1: Tabla empieza (X) vs Minimax (O)
    print("Partida 1: IA Tabla (X) vs IA Minimax (O)...", end=" ")
    winner1, moves1 = simulate_game("table", "minimax", table_ai)
    result1 = "EMPATE" if (winner1 == 0 or winner1 is None) else f"GANÓ {winner1}"
    print(f"Resultado: {result1} en {moves1} jugadas.")

    # Prueba 2: Minimax empieza (X) vs Tabla (O)
    print("Partida 2: IA Minimax (X) vs IA Tabla (O)...", end=" ")
    winner2, moves2 = simulate_game("minimax", "table", table_ai)
    result2 = "EMPATE" if (winner2 == 0 or winner2 is None) else f"GANÓ {winner2}"
    print(f"Resultado: {result2} en {moves2} jugadas.")

    print("-" * 40)

    # Verificación final
    if result1 == "EMPATE" and result2 == "EMPATE":
        print("✅ ÉXITO: Ambos juegan perfecto. La tabla es idéntica al minimax.")
    else:
        print("❌ ALERTA: Se detectó una victoria. Uno de los dos no es perfecto.")
        print("Revisa si el minimax_alpha_beta está configurado para el ID de jugador correcto.")


if __name__ == "__main__":
    main()
