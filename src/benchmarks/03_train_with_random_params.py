import csv
import os
import random
import time

from src.ai.ql_agent import QLearningAgent
from src.benchmarks.utils import evaluate_vs_minimax
from src.training.gym import train_with_decay

NUM_AGENTS = 5
MILESTONES = [100, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 500000, 1000000]
CSV_OUTPUT = "queries/01_results.csv"


def run_experiment():
    headers = ["agent_id", "alpha", "gamma", "decay", "r_draw", "episodes_total", "wins", "losses", "draws", "time_sec"]

    with open(CSV_OUTPUT, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for i in range(1, NUM_AGENTS + 1):
            alpha = round(random.uniform(0.1, 0.5), 3)
            gamma = round(random.uniform(0.3, 0.9), 3)
            r_draw = 0.5

            print(f"\n>>> Iniciando Agente {i}/{NUM_AGENTS}")
            print(f"Parámetros: alpha={alpha}, gamma={gamma}")

            agent = QLearningAgent(alpha=alpha, gamma=gamma, epsilon=1.0)

            total_trained_episodes = 0
            start_time = time.time()

            for m in MILESTONES:
                episodes_to_run = m - total_trained_episodes

                agent, _ = train_with_decay(
                    agent, episodes=episodes_to_run, epsilon_decay_gen=0.01, reward_draw_gen=r_draw
                )

                total_trained_episodes = m

                wins, losses, draws = evaluate_vs_minimax(agent, num_games=50)

                elapsed = time.time() - start_time
                print(f"[{m} eps] W: {wins} | L: {losses} | D: {draws} | Time: {elapsed:.2f}s")

                # 5. Guardar resultados en el CSV
                writer.writerow(
                    {
                        "agent_id": i,
                        "alpha": alpha,
                        "gamma": gamma,
                        "decay": 0.01,
                        "r_draw": r_draw,
                        "episodes_total": m,
                        "wins": wins,
                        "losses": losses,
                        "draws": draws,
                        "time_sec": round(elapsed, 2),
                    }
                )
                file.flush()


if __name__ == "__main__":
    if not os.path.exists("tictactoe_lookup.pkl"):
        print("Advertencia: tictactoe_lookup.pkl no encontrado. La evaluación será más lenta.")

    run_experiment()
    print(f"\nProceso finalizado. Resultados guardados en {CSV_OUTPUT}")
