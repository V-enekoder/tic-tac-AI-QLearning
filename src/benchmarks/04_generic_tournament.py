import csv
import os
import random
import time

from src.ai.ql_agent import QLearningAgent
from src.benchmarks.utils import evaluate_vs_minimax
from src.training.gym import train_with_decay

FINAL_ALPHA = 0.6500
FINAL_GAMMA = 0.0300
FINAL_DECAY = 0.006400
FINAL_R_DRAW = 0.50
NUM_GAMES_TORNEO = 100

OUTPUT_DIR = "queries/generic_tournament"
CSV_FILE = os.path.join(OUTPUT_DIR, "generic_tournament_results.csv")


def evaluate_vs_random(ql_agent: QLearningAgent, num_games=100) -> tuple:
    """Evalúa el agente QL contra un agente que juega completamente al azar."""
    ql_agent.epsilon = 0.0
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
                move = random.choice(board.get_available_moves())

            if move:
                board.make_move(move[0], move[1])

        if board.winner == 0 or board.winner is None:
            draws += 1
        elif (board.winner == 1 and ql_is_p1) or (board.winner == 2 and not ql_is_p1):
            wins += 1
        else:
            losses += 1

    return wins, losses, draws


def evaluate_vs_self(ql_agent: QLearningAgent, num_games=100) -> tuple:
    """Evalúa el agente QL contra una copia de sí mismo (para medir estabilidad de política)."""

    ql_agent.epsilon = 0.0
    wins, losses, draws = 0, 0, 0

    for i in range(num_games):
        board = Board()

        while not board.game_over:
            move = ql_agent.choose_action(board)

            if move:
                board.make_move(move[0], move[1])

        if board.winner == 0 or board.winner is None:
            draws += 1
        elif board.winner == 1 or board.winner == 2:
            wins += 1 if board.winner == 1 else 0
            losses += 1 if board.winner == 2 else 0

    return wins, losses, draws


def run_generic_tournament():
    print("\n--- INICIANDO TORNEO GENÉRICO DE RENDIMIENTO ---")
    print(f"HPs: α={FINAL_ALPHA}, γ={FINAL_GAMMA}, decay={FINAL_DECAY}")

    ql_agent = QLearningAgent(alpha=FINAL_ALPHA, gamma=FINAL_GAMMA, epsilon=1.0)

    print(f"1. Entrenando agente para obtener la política óptima (hasta {MAX_EPISODES} episodios)...")
    ql_agent, _ = train_with_decay(
        ql_agent, episodes=MAX_EPISODES, epsilon_decay_gen=FINAL_DECAY, reward_draw_gen=FINAL_R_DRAW
    )
    print("   -> Entrenamiento completado.")

    scenarios = [
        {"name": "Vs_Random", "function": evaluate_vs_random},
        {"name": "Vs_Minimax", "function": evaluate_vs_minimax},
        {"name": "Vs_Self", "function": evaluate_vs_self},
    ]

    tournament_results = []

    for scenario in scenarios:
        print(f"2. Ejecutando Escenario: {scenario['name']} ({NUM_GAMES_TORNEO} partidas)...")

        start = time.time()
        wins, losses, draws = scenario["function"](ql_agent, num_games=NUM_GAMES_TORNEO)
        end = time.time()

        tournament_results.append(
            {
                "Scenario": scenario["name"],
                "W": wins,
                "L": losses,
                "D": draws,
                "Success_Rate": (wins + draws) / NUM_GAMES_TORNEO,
                "Time_s": round(end - start, 2),
            }
        )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(CSV_FILE, mode="w", newline="") as csvfile:
        fieldnames = ["Scenario", "W", "L", "D", "Success_Rate", "Time_s"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in tournament_results:
            writer.writerow(row)

    print("\n--- RESULTADOS DEL TORNEO ---")
    print(f"{'Escenario':<15}{'W':>5}{'L':>5}{'D':>5}{'Success %':>12}")
    print("-" * 42)
    for result in tournament_results:
        success_perc = result["Success_Rate"] * 100
        print(f"{result['Scenario']:<15}{result['W']:>5}{result['L']:>5}{result['D']:>5}{success_perc:>11.2f}%")

    print(f"\nDatos guardados en {CSV_FILE}")


MAX_EPISODES = 6500

if __name__ == "__main__":
    from src.game_logic.board import Board

    run_generic_tournament()
