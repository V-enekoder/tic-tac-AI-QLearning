from src.ai.qlearning import QLearningAgent
from src.game_logic.board import Board


def train(episodes=20000):
    board = Board()
    agent = QLearningAgent()

    for episode in range(episodes):
        board.reset()

        history = {1: None, 2: None}

        while not board.game_over:
            current_player = board.turn
            state = agent.get_state_key(board.board)
            action = agent.choose_action(board)

            history[current_player] = (state, action)

            board.make_move(action[0], action[1])

            if board.game_over:
                if board.winner != 0:
                    agent.learn(state, action, 1, None, [], True)

                    other_player = 2 if current_player == 1 else 1
                    prev_state, prev_action = history[other_player]

                    agent.learn(prev_state, prev_action, -1, state, [], True)
                else:
                    for p in [1, 2]:
                        s, a = history[p]
                        agent.learn(s, a, 0.5, None, [], True)
            else:
                other_player = 2 if current_player == 1 else 1
                if history[other_player] is not None:
                    prev_state, prev_action = history[other_player]
                    current_board_state = agent.get_state_key(board.board)
                    agent.learn(prev_state, prev_action, 0, current_board_state, board.get_available_moves(), False)

    return agent
