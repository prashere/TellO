import random
from state import *
from q_learning import *
from actions import *

class Environment:
    def __init__(self, q_learning: QLearning):
        """
        Initializes the environment with a Q-learning agent.
        :param q_learning: The Q-learning agent managing action selection and learning.
        """
        self.q_learning = q_learning

    def get_reward(self, state: State) -> float:
        """
        Computes a reward based on the engagement and learning progress.
        :param state: The current state.
        :return: A reward value.
        """
        engagement_score = {
            EngagementLevel.HIGH: 1.0,
            EngagementLevel.MEDIUM: 0.5,
            EngagementLevel.LOW: 0.0
        }[state.engagement_level]

        learning_score = min(state.vocabulary_usage / 5, 1.0)  # Normalize usage (assuming 5 is a good usage level)

        return 0.5 * engagement_score + 0.5 * learning_score

    def transition(self, state: State, action: Action) -> State:
        """
        Simulates the state transition after an action.
        :param state: The current state.
        :param action: The action taken.
        :return: The next state.
        """
        new_confidence = random.choice(list(Confidence))
        new_prompt_necessity = random.choice(list(PromptNecessity))
        new_response_length = random.choice(list(ResponseLength))
        new_vocabulary_usage = max(0, state.vocabulary_usage + (1 if action.lexical_type == LexicalType.KNOWN else -1))
        new_engagement_level = random.choice(list(EngagementLevel))
        new_emotional_state = random.choice(list(EmotionalState))

        return State(new_confidence, new_prompt_necessity, new_response_length,
                     new_vocabulary_usage, new_engagement_level, new_emotional_state)

    def run_episode(self, initial_state: State, num_steps: int = 10):
        """
        Runs a full episode of interaction.
        :param initial_state: The starting state.
        :param num_steps: The number of steps to simulate.
        """
        state = initial_state

        for _ in range(num_steps):
            action = self.q_learning.choose_action(state)
            next_state = self.transition(state, action)
            reward = self.get_reward(next_state)
            self.q_learning.update_q_value(state, action, reward, next_state)
            state = next_state

            print(f"Action: {action}, Reward: {reward}, New State: {state}")

# Example Usage:
q_learning_agent = QLearning(actions)
env = Environment(q_learning_agent)

# Define an initial state
initial_state = State(Confidence.MEDIUM, PromptNecessity.NO, ResponseLength.MEDIUM, 3, EngagementLevel.MEDIUM, EmotionalState.NEUTRAL)
env.run_episode(initial_state)
