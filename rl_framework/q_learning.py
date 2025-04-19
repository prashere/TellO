import random
import pickle
import os
from typing import List
from .state import State
from .actions import Action


class QLearning:
    def __init__(self, actions: List[Action], alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.2, q_table_path="rl_framework/table/q_table.pkl"):
        """
        Initializes the Q-learning agent.

        :param actions: List of all possible actions.
        :param alpha: Learning rate.
        :param gamma: Discount factor.
        :param epsilon: Exploration rate (ϵ-greedy strategy).
        :param q_table_path: Path to saved Q-table.
        """
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}
        self.q_table_path = q_table_path
        self.load_q_table()  # Load pre-trained Q-values if available

    
    def _get_q_values(self, state: State) -> List[float]:
        """
        Returns the list of Q-values for the given state.
        Ensures Q-values are initialized correctly.
        """
        state_key = state.to_tuple()

        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0 for _ in self.actions]

        q_values = self.q_table[state_key]

        # Debugging print
        # print(f"Getting Q-values for state: {state_key}")
        # print(f"Actions: {self.actions}")
        # print(f"Q-values (length {len(q_values)}): {q_values}")

        if len(q_values) != len(self.actions):
            print(f"WARNING: Fixing Q-values length mismatch!")
            self.q_table[state_key] = [0.0 for _ in self.actions]
            return self.q_table[state_key]

        return q_values

    def choose_action(self, state: State) -> Action:
        """
        Chooses an action using an epsilon-greedy strategy.
        """
        q_values = self._get_q_values(state)

        if random.random() < self.epsilon:
            return random.choice(self.actions)  # Exploration step

        max_q = max(q_values)
        best_actions = [action for action, q in zip(
            self.actions, q_values) if q == max_q]

        if not best_actions:  # Fallback in case of an empty list
            return random.choice(self.actions)

        return random.choice(best_actions)

    def update_q_value(self, state: State, action: Action, reward: float, next_state: State) -> None:
        """
        Updates the Q-value for a state-action pair using the Q-learning update rule.
        """
        state_key = state.to_tuple()

        if action not in self.actions:
            raise ValueError(
                f"Action {action} not found in self.actions list.")

        action_index = self.actions.index(action)

        q_values = self._get_q_values(state)
        if not q_values:
            # Initialize Q-values if missing
            q_values = [0] * len(self.actions)

        if action_index >= len(q_values):
            raise IndexError(
                f"Action index {action_index} is out of range for Q-values {q_values}")

        current_q = q_values[action_index]

        next_q_values = self._get_q_values(next_state)
        if not next_q_values:
            # Initialize Q-values if missing
            next_q_values = [0] * len(self.actions)

        max_next_q = max(next_q_values)

        new_q = current_q + self.alpha * \
            (reward + self.gamma * max_next_q - current_q)

        self.q_table[state_key][action_index] = new_q

    def get_best_action(self, state: State) -> Action:
        """
        Retrieves the best action (the one with the highest Q-value) for a given state.
        """
        q_values = self._get_q_values(state)
        max_q = max(q_values)
        best_actions = [action for action, q in zip(
            self.actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def load_q_table(self):
        """
        Loads the Q-table from the file if available.
        """
        if os.path.exists(self.q_table_path):
            with open(self.q_table_path, "rb") as file:
                self.q_table = pickle.load(file)
            print(f"Q-table loaded from {self.q_table_path}")
            # Debug: Check first 5 keys
            print(f"Q-table keys: {list(self.q_table.keys())[:5]}")
        else:
            print("No saved Q-table found. Starting fresh.")

    def save_q_table(self):
        """
        Saves the Q-table to a file.
        """
        os.makedirs(os.path.dirname(self.q_table_path), exist_ok=True)
        with open(self.q_table_path, "wb") as file:
            pickle.dump(self.q_table, file)
        print(f"Q-table saved to {self.q_table_path}")
