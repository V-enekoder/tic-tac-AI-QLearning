import os
import pickle

from src.game_logic.board import Board


def get_board_hash(board_matrix):
    """Misma función de hash utilizada en la precomputación."""
    return tuple(item for row in board_matrix for item in row)


class TableAIPlayer:
    def __init__(self, pickle_path="tictactoe_lookup.pkl"):
        if not os.path.exists(pickle_path):
            raise FileNotFoundError(f"No se encontró {pickle_path}. ¡Debes generarlo primero!")

        with open(pickle_path, "rb") as f:
            self.lookup_table = pickle.load(f)
        print(f"Tabla cargada con {len(self.lookup_table)} estados.")

    def get_move(self, board: Board):
        state_hash = get_board_hash(board.board)
        # La tabla guarda el movimiento directamente o un dict con 'move'
        data = self.lookup_table.get(state_hash)

        if data is None:
            return None

        # Dependiendo de cómo guardaste el objeto:
        if isinstance(data, dict):
            return data["move"]
        return data


def print_board(board):
    symbols = {0: " ", 1: "X", 2: "O"}
    for i, row in enumerate(board.board):
        display_row = [symbols[cell] for cell in row]
        print(f" {display_row[0]} | {display_row[1]} | {display_row[2]} ")
        if i < 2:
            print("-----------")


def play_game():
    board = Board()
    try:
        ai = TableAIPlayer("tictactoe_lookup.pkl")
    except Exception as e:
        print(e)
        return

    print("\n--- TicTacToe: Humano (X) vs IA Tabla (O) ---")
    print("Las coordenadas son de 0 a 2 (ejemplo: 0 0 para la esquina superior izquierda)\n")

    # Supongamos que Humano es 1 (X) y AI es 2 (O)
    # Si tu Board empieza siempre con el jugador 1:
    while not board.game_over:
        print_board(board)

        if board.turn == 1:  # Turno Humano
            try:
                move_str = input("\nTu movimiento (fila col): ")
                r, c = map(int, move_str.split())
                if (r, c) not in board.get_available_moves():
                    print("Movimiento no válido. Intenta de nuevo.")
                    continue
                board.make_move(r, c)
            except ValueError:
                print("Entrada inválida. Usa el formato: 0 1")
                continue
        else:  # Turno IA
            print("\nIA pensando (consultando tabla)...")
            move = ai.get_move(board)
            if move:
                print(f"IA elige: {move}")
                board.make_move(move[0], move[1])
            else:
                print("La IA no encontró este estado en la tabla. ¿Se precomputó correctamente?")
                break

    print_board(board)
    if board.winner == 0 or board.winner is None:
        print("\n¡Empate!")
    else:
        winner_name = "Humano" if board.winner == 1 else "IA"
        print(f"\n¡El ganador es: {winner_name}!")


if __name__ == "__main__":
    play_game()
