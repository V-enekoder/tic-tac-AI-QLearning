import pickle

from src.game_logic.board import Board


class TicTacToeSmartAI:
    def __init__(self, pickle_path="tictactoe_lookup.pkl"):
        try:
            with open(pickle_path, "rb") as f:
                self.lookup_table = pickle.load(f)
        except FileNotFoundError:
            print("Error: Archivo pickle no encontrado. Ejecuta la precomputación primero.")
            self.lookup_table = {}

    def get_best_move(self, board: Board):
        state_hash = tuple(item for row in board.board for item in row)
        # Retorna el movimiento precalculado
        return self.lookup_table.get(state_hash)
