import os
import random
import time
import pickle
from collections import deque
from typing import List
import numpy as np

from q_learning import QLearning
from state import *
from actions import Action
from environment import Environment

class ReplayBuffer:
    def __init__(self, capacity: int = 5000):
        """Initialize the replay buffer with a given capacity."""
        self.buffer = deque(maxlen=capacity)

    def add(self, state: State, action: Action, reward: float, next_state: State):
        """Add an experience tuple to the buffer."""
        self.buffer.append((state, action, reward, next_state))

    def sample(self, batch_size: int):
        """Return a random sample of experiences."""
        sample_size = min(len(self.buffer), batch_size)
        return random.sample(self.buffer, sample_size)

    def size(self) -> int:
        return len(self.buffer)

class Trainer:
    def __init__(self, q_learning_agent: QLearning, environment: Environment, num_episodes: int = 1000,
                 steps_per_episode: int = 10, batch_size: int = 32,
                 epsilon_decay: float = 0.995, epsilon_min: float = 0.05,
                 evaluation_interval: int = 100):
        """
        Initialize the Trainer with the Q-learning agent, environment, and training hyperparameters.
        :param q_learning_agent: The Q-learning agent.
        :param environment: The simulated environment.
        :param num_episodes: Number of episodes for training.
        :param steps_per_episode: Steps per episode (each episode simulates one storytelling session).
        :param batch_size: Number of experiences to sample for mini-batch updates.
        :param epsilon_decay: Decay rate for epsilon.
        :param epsilon_min: Minimum epsilon.
        :param evaluation_interval: Number of episodes between evaluations/saves.
        """
        self.agent = q_learning_agent
        self.env = environment
        self.num_episodes = num_episodes
        self.steps_per_episode = steps_per_episode
        self.batch_size = batch_size
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.evaluation_interval = evaluation_interval
        
        self.replay_buffer = ReplayBuffer(capacity=5000)
        self.rewards_history = []  # To log cumulative reward per episode

    def train(self):
        """
        Train the Q-learning agent using experience replay.
        """
        for episode in range(1, self.num_episodes + 1):
            # Reset the environment to obtain an initial state.
            state = self.env.reset()  # Ensure that Environment.reset() returns an initial State.
            episode_reward = 0.0

            for step in range(self.steps_per_episode):
                # Choose an action using epsilon-greedy strategy.
                action = self.agent.choose_action(state)
                next_state = self.env.transition(state, action)
                reward = self.env.get_reward(state, action)
                
                # Store the transition in the replay buffer.
                self.replay_buffer.add(state, action, reward, next_state)
                episode_reward += reward
                
                # Update Q-values using a mini-batch of experiences if enough samples are available.
                if self.replay_buffer.size() >= self.batch_size:
                    batch = self.replay_buffer.sample(self.batch_size)
                    for s, a, r, s_next in batch:
                        self.agent.update_q_value(s, a, r, s_next)
                
                # Transition to the next state.
                state = next_state

            # Decay epsilon for exploration.
            self.agent.epsilon = max(self.agent.epsilon * self.epsilon_decay, self.epsilon_min)
            self.rewards_history.append(episode_reward)
            print(f"Episode {episode}/{self.num_episodes} Reward: {episode_reward:.2f}, Epsilon: {self.agent.epsilon:.3f}")

            # Periodically evaluate and save the model.
            if episode % self.evaluation_interval == 0:
                self.evaluate(num_trials=5)
                self.save_q_table(f"q_table_episode_{episode}.pkl")

        print("Training complete.")

    def evaluate(self, num_trials: int = 10):
        """
        Evaluate the current policy without exploration (epsilon=0).
        :param num_trials: Number of evaluation episodes.
        """
        original_epsilon = self.agent.epsilon
        self.agent.epsilon = 0.0  # Turn off exploration for evaluation.
        total_reward = 0.0

        for trial in range(num_trials):
            state = self.env.reset()
            trial_reward = 0.0
            for step in range(self.steps_per_episode):
                action = self.agent.get_best_action(state)
                next_state = self.env.transition(state, action)
                reward = self.env.get_reward(state, action)
                trial_reward += reward
                state = next_state
            total_reward += trial_reward

        avg_reward = total_reward / num_trials
        print(f"Evaluation over {num_trials} trials: Average Reward: {avg_reward:.2f}")
        self.agent.epsilon = original_epsilon  # Restore exploration rate.

    def save_q_table(self, filename: str = "q_table.pkl"):
        """
        Save the Q-table to a file.
        :param filename: The file name.
        """
        filename = "./rl_framework/table/" + filename
        os.makedirs('./rl_framework/table', exist_ok=True)
        with open(filename, "wb") as f:
            pickle.dump(self.agent.q_table, f)
        print(f"Q-table saved to {filename}")

    def load_q_table(self, filename: str = "q_table.pkl"):
        """
        Load the Q-table from a file.
        :param filename: The file name.
        """
        try:
            filename = "./rl_framework/table/" + filename
            os.makedirs('./rl_framework/table', exist_ok=True)
            with open(filename, "rb") as f:
                self.agent.q_table = pickle.load(f)
            print(f"Q-table loaded from {filename}")
        except FileNotFoundError:
            print("No saved Q-table found. Starting with an empty Q-table.")

    def reset_training_data(self):
        """
        Reset the training data, including the replay buffer and rewards history.
        """
        self.replay_buffer = ReplayBuffer(capacity=5000)
        self.rewards_history = []

# -------------------------
# Example Usage:

if __name__ == "__main__":
    # Import your actions, for instance:
    from actions import Action, SentenceComplexity, LexicalType, ClarificationType

    # Define actions (you can extend this list as needed)
    actions = [
        Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.SIMPLE, lexical_type=LexicalType.KNOWN),
        Action(action_type="Clarification", clarification_type=ClarificationType.SENTENCE_REPETITION),
        # You can add more actions here...
    ]
    
    # Create the Q-learning agent with the action space.
    q_learning_agent = QLearning(actions)
    
    # Create the environment with the Q-learning agent.
    env = Environment(q_learning_agent)
    
    # Define an initial state for INTERACTION mode (example).
    initial_state = State(
        mode=Mode.INTERACTION,
        engagement_level=EngagementLevel.MEDIUM,
        emotional_state=EmotionalState.HAPPY,
        response_quality=ResponseQuality.AVERAGE,
        prompt_necessity=PromptNecessity.YES,
        response_length=ResponseLength.MEDIUM,
        vocabulary_usage=VocabularyUsage.MEDIUM,
        wh_question_detected=False
    )
    
    # Initialize and run the trainer.
    trainer = Trainer(q_learning_agent, env, num_episodes=100, steps_per_episode=10, batch_size=32)
    trainer.train()
    trainer.evaluate(num_trials=5)
    trainer.save_q_table("final_q_table.pkl")
