import random

from src.ai.qlearning import QLearningAgent


class GeneticQLAgent:
    def __init__(self, agent_id, gen=None):
        self.id = agent_id
        self.agent = None  # Instancia de QLearningAgent
        self.fitness = 0.0

        # El Cromosoma (α, γ, epsilon_final, N_episodes)
        if gen is None:
            # Generación aleatoria de los genes iniciales
            self.alpha = round(random.uniform(0.01, 0.99), 2)
            self.gamma = round(random.uniform(0.01, 0.99), 2)
            self.epsilon_decay_rate = round(random.uniform(0.0001, 0.01), 4)  # Un factor para el decay
        else:
            self.alpha, self.gamma, self.epsilon_decay_rate = gen

    def instantiate_agent(self):
        self.agent = QLearningAgent(alpha=self.alpha, gamma=self.gamma, epsilon=1.0)
