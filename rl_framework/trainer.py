import random
import numpy as np
from q_learning import QLearning
from environment import Environment

class Trainer:
    def __init__(self, q_learning_agent, environment, episodes=1000, max_steps=50, decay_rate=0.99):
        """
        Initializes the trainer for reinforcement learning.
        
        :param q_learning_agent: The Q-learning agent (TellO).
        :param environment: The environment handling interactions.
        :param episodes: Number of training episodes.
        :param max_steps: Maximum steps per episode.
        :param decay_rate: Decay rate for epsilon (exploration) and learning rate.
        """
        self.agent = q_learning_agent
        self.env = environment
        self.episodes = episodes
        self.max_steps = max_steps
        self.decay_rate = decay_rate  # Decay factor for epsilon and alpha
        self.rewards_per_episode = []  # Track rewards to monitor learning progress

    def train(self):
        """Runs the training loop for the reinforcement learning framework."""
        for episode in range(1, self.episodes + 1):
            state = self.env.reset()  # Get initial state
            total_reward = 0  # Track total reward for this episode
            step = 0  # Step counter

            for step in range(self.max_steps):
                # Choose action using epsilon-greedy policy
                action = self.agent.choose_action(state)

                # Execute the action in the environment
                next_state, reward, done = self.env.step(action)

                # Update Q-values using Q-learning update rule
                self.agent.update_q_value(state, action, reward, next_state)

                # Move to the next state
                state = next_state
                total_reward += reward

                if done:  # Stop if terminal state is reached
                    break

            # Store rewards for tracking progress
            self.rewards_per_episode.append(total_reward)

            # Decay epsilon (exploration) and learning rate (alpha) over time
            self.agent.epsilon *= self.decay_rate
            self.agent.alpha *= self.decay_rate

            # Logging to monitor training progress
            if episode % 100 == 0 or episode == 1:
                avg_reward = np.mean(self.rewards_per_episode[-100:])
                print(f"Episode {episode}/{self.episodes} - Avg Reward (Last 100): {avg_reward:.2f}, Steps Taken: {step}, Epsilon: {self.agent.epsilon:.4f}")

        print("Training Complete! 🚀")

    def get_training_results(self):
        """Returns training statistics."""
        return {
            "total_episodes": self.episodes,
            "final_epsilon": self.agent.epsilon,
            "final_learning_rate": self.agent.alpha,
            "average_reward_last_100": np.mean(self.rewards_per_episode[-100:]),
            "reward_history": self.rewards_per_episode
        }

# Example Usage
trainer = Trainer(q_learning_agent=q_learning_agent, environment=environment, episodes=1000)
trainer.train()
results = trainer.get_training_results()
print(results)
