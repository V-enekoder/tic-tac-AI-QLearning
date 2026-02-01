import csv
import os
import random
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.ai.ql_agent import GeneticQLAgent
from src.benchmarks.utils import evaluate_vs_minimax
from src.training.gym import train_with_decay

POPULATION_SIZE = 50
GENERATIONS = 30
TOUR_SIZE = 15
MAX_WORKERS = 6
NUM_GAMES = 50
NUM_EPISODES = 6500
NUM_ELITES = 5
MUTATION_START_RATE = 0.10
MUTATION_END_RATE = 0.01


def initialize_population():
    return [GeneticQLAgent(i) for i in range(POPULATION_SIZE)]


def save_results_to_csv(population, generation, filename="genetic_results.csv"):
    """
    Guarda los datos de toda la población de una generación en un archivo CSV.
    """
    file_exists = os.path.isfile(filename)

    with open(filename, mode="a", newline="") as csvfile:
        fieldnames = [
            "generation",
            "agent_id",
            "alpha",
            "gamma",
            "decay",
            "reward_draw",
            "fitness",
            "episodes_to_optimal",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()  # Solo escribe la cabecera la primera vez

        for agent in population:
            writer.writerow(
                {
                    "generation": generation,
                    "agent_id": agent.id,
                    "alpha": agent.alpha,
                    "gamma": agent.gamma,
                    "decay": agent.epsilon_decay_rate,
                    "reward_draw": agent.reward_draw,
                    "fitness": round(agent.fitness, 4),
                    "episodes_to_optimal": agent.episodes_to_optimal,
                }
            )


def evaluate_individual_task(individual_data, generation_num, total_generations, individual_index, total_individuals):
    """
    Función que realiza el entrenamiento y la evaluación de un solo agente.
    """
    individual = individual_data["agent"]
    episodes = individual_data["episodes"]
    num_games = individual_data["num_games"]
    reward_draw_gen = individual.reward_draw
    decay_rate_gen = individual.epsilon_decay_rate
    """
    print(
        f"  [G{generation_num}/{total_generations} - Agente {individual_index + 1:02d}/{total_individuals}] "
        f"Evaluando α={individual.alpha:.2f}, γ={individual.gamma:.2f}..."
    )
    """

    individual.instantiate_agent()
    individual.agent, episodes_to_optimal = train_with_decay(
        individual.agent, episodes=episodes, epsilon_decay_gen=decay_rate_gen, reward_draw_gen=reward_draw_gen
    )
    wins, _, draws = evaluate_vs_minimax(individual.agent, num_games=num_games)
    quality_fitness = (wins + draws) / num_games

    speed_bonus = (episodes - episodes_to_optimal) / episodes

    individual.episodes_to_optimal = episodes_to_optimal

    if quality_fitness < 1.0:
        individual.fitness = quality_fitness
    else:
        speed_bonus = (NUM_EPISODES - episodes_to_optimal) / NUM_EPISODES
        individual.fitness = 1.0 + max(0, speed_bonus)

    log_line = (
        f"  [G{generation_num}/{total_generations} - Agente {individual_index + 1:02d}/{total_individuals}] "
        f"Evaluando α={individual.alpha:.2f}, γ={individual.gamma:.2f} "
        f"-> FITNESS: {individual.fitness:.3f} (D:{draws} L:{num_games - wins - draws}) "
        f"[CONV: {episodes_to_optimal}/{episodes}]"
    )

    return individual, log_line


def evaluate_population(population, generation_num, total_generations):
    total_individuals = len(population)

    tasks = []
    for i, individual in enumerate(population):
        task_data = {
            "agent": individual,
            "episodes": NUM_EPISODES,
            "num_games": NUM_GAMES,
        }
        tasks.append((task_data, generation_num, total_generations, i, total_individuals))

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_agent = {executor.submit(evaluate_individual_task, *task): i for i, task in enumerate(tasks)}

        for future in as_completed(future_to_agent):
            updated_individual, log_line = future.result()
            original_index = future_to_agent[future]
            population[original_index] = updated_individual

            print(log_line)


def selection(population):
    best = None
    for _ in range(TOUR_SIZE):
        candidate = random.choice(population)
        if best is None or candidate.fitness > best.fitness:
            best = candidate
    return best


def crossover(parent1, parent2, mutation_rate=0.1):
    p1 = [parent1.alpha, parent1.gamma, parent1.epsilon_decay_rate]
    p2 = [parent2.alpha, parent2.gamma, parent2.epsilon_decay_rate]

    crossover_point = random.randint(1, len(p1) - 1)
    child_gen = p1[:crossover_point] + p2[crossover_point:]

    # Mutación
    for i in range(len(child_gen)):
        if random.random() < mutation_rate:
            if i == 0:
                child_gen[i] = round(random.uniform(0.01, 0.99), 2)
            elif i == 1:
                child_gen[i] = round(random.uniform(0.01, 0.99), 2)
            elif i == 2:
                child_gen[i] = round(random.uniform(0.0001, 0.01), 4)

    return GeneticQLAgent(0, gen=child_gen)


def run_genetic_algorithm():
    population = initialize_population()
    best_overall = None

    csv_filename = f"queries/genetic_experiment_{int(time.time())}.csv"

    for generation in range(GENERATIONS):  # GENERATIONS es el total
        print(f"\n--- GENERACIÓN {generation + 1}/{GENERATIONS} ---")

        evaluate_population(population, generation + 1, GENERATIONS)

        save_results_to_csv(population, generation + 1, csv_filename)

        population.sort(key=lambda x: x.fitness, reverse=True)

        current_best = population[0]
        if best_overall is None or current_best.fitness > best_overall.fitness:
            best_overall = current_best

        new_population = []

        new_population.extend(population[:NUM_ELITES])

        current_mutation_rate = max(
            MUTATION_END_RATE,
            MUTATION_START_RATE - (MUTATION_START_RATE - MUTATION_END_RATE) * (generation / GENERATIONS),
        )

        while len(new_population) < POPULATION_SIZE:
            parent1 = selection(
                population,
            )
            parent2 = selection(population)
            child = crossover(parent1, parent2, current_mutation_rate)
            new_population.append(child)

        population = new_population
        for i, agent in enumerate(population):
            agent.id = i

    print("\n--- RESULTADO FINAL ---")
    print(f"Mejor Agente Global: Fitness={best_overall.fitness:.3f}")

    print(
        f"Hyperparámetros Óptimos: α={best_overall.alpha:.2f}, "
        f"γ={best_overall.gamma:.2f}, "
        f"decay={best_overall.epsilon_decay_rate}, "
        f"R_draw={best_overall.reward_draw:.2f}"
    )


if __name__ == "__main__":
    inicio = time.time()
    run_genetic_algorithm()
    fin = time.time()
    print(fin - inicio)

# Mejor Agente Global: Fitness=1.446
# Hyperparámetros Óptimos: α=0.27, γ=0.63, decay=0.0045, R_draw=0.50
