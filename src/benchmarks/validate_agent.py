import csv
import math
import os
import statistics
import time

from src.ai.ql_agent import QLearningAgent
from src.benchmarks.utils import evaluate_vs_minimax
from src.training.gym import train_with_decay

FINAL_ALPHA = 0.6500
FINAL_GAMMA = 0.0300
FINAL_DECAY = 0.006400

FINAL_R_DRAW = 0.50
NUM_EPISODES = 6500
NUM_GAMES_EVAL = 50
NUM_VALIDATION_RUNS = 30
OUTPUT_DIR = "queries/validate-agent"
CSV_VALIDATION_FILE = os.path.join(OUTPUT_DIR, f"validation_results_{int(time.time())}.csv")  # Archivo de salida


def validate_optimal_agent():
    """Entrena y evalúa al agente con los HPs fijos NUM_VALIDATION_RUNS veces, registrando los resultados."""

    all_hybrid_fitness = []

    # Configuración de CSV
    fieldnames = [
        "run_id",
        "alpha",
        "gamma",
        "decay",
        "r_draw",
        "episodes_budget",
        "episodes_to_optimal",
        "final_fitness",
        "wins",
        "losses",
        "draws",
    ]

    with open(CSV_VALIDATION_FILE, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        print(f"\n--- VALIDACIÓN FINAL: {NUM_VALIDATION_RUNS} RÉPLICAS ---")
        print(f"HPs a Probar: α={FINAL_ALPHA}, γ={FINAL_GAMMA}, decay={FINAL_DECAY}, R_draw={FINAL_R_DRAW}")
        print(f"Resultados de cada réplica se guardarán en: {CSV_VALIDATION_FILE}")

        for i in range(NUM_VALIDATION_RUNS):
            print(f"\n[Réplica {i + 1}/{NUM_VALIDATION_RUNS}] Entrenando...")

            agent = QLearningAgent(alpha=FINAL_ALPHA, gamma=FINAL_GAMMA, epsilon=1.0)

            agent, episodes_to_optimal = train_with_decay(
                agent, episodes=NUM_EPISODES, epsilon_decay_gen=FINAL_DECAY, reward_draw_gen=FINAL_R_DRAW
            )

            wins, losses, draws = evaluate_vs_minimax(agent, num_games=NUM_GAMES_EVAL)
            quality_fitness = (wins + draws) / NUM_GAMES_EVAL

            speed_bonus = (NUM_EPISODES - episodes_to_optimal) / NUM_EPISODES

            if quality_fitness < 1.0:
                final_hybrid_fitness = quality_fitness
            else:
                final_hybrid_fitness = quality_fitness + max(0, speed_bonus)

            all_hybrid_fitness.append(final_hybrid_fitness)

            print(
                f"  -> Fitness: {final_hybrid_fitness:.4f} (L: {losses}) [Conv: {episodes_to_optimal}/{NUM_EPISODES}]"
            )

            writer.writerow(
                {
                    "run_id": i + 1,
                    "alpha": FINAL_ALPHA,
                    "gamma": FINAL_GAMMA,
                    "decay": FINAL_DECAY,
                    "r_draw": FINAL_R_DRAW,
                    "episodes_budget": NUM_EPISODES,
                    "episodes_to_optimal": episodes_to_optimal,
                    "final_fitness": round(final_hybrid_fitness, 6),
                    "wins": wins,
                    "losses": losses,
                    "draws": draws,
                }
            )
            csvfile.flush()

    mean_fitness = statistics.mean(all_hybrid_fitness)
    try:
        stdev_fitness = statistics.stdev(all_hybrid_fitness)
    except statistics.StatisticsError:
        stdev_fitness = 0.0

    print("\n" + "=" * 50)
    print("      RESULTADOS ESTADÍSTICOS DE LA VALIDACIÓN")
    print("=" * 50)
    print(f"Media del Fitness Híbrido:   {mean_fitness:.4f}")
    print(f"Desviación Estándar (DS):    {stdev_fitness:.5f}")
    print(f"Mejor Pico (Máx):            {max(all_hybrid_fitness):.4f}")
    print("\nConclusión para el Reporte:")
    if stdev_fitness < 0.005:
        print("  El conjunto de HPs es EXTREMADAMENTE ESTABLE (DS < 0.005).")
    elif stdev_fitness < 0.02:
        print("  El conjunto de HPs es Robusto y sus variaciones son mínimas.")
    else:
        print("  El conjunto de HPs es Robusto pero presenta cierta volatilidad.")


if __name__ == "__main__":
    inicio = time.time()
    validate_optimal_agent()
    fin = time.time()
    print(f"\nTiempo total de validación: {fin - inicio:.2f} segundos")
