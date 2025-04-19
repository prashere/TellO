import random
from .environment import Environment
from .q_learning import QLearning
from .state import State, Mode, EngagementLevel, EmotionalState, ResponseQuality, PromptNecessity, ResponseLength, VocabularyUsage


class Trainer:
    def __init__(self, q_learning: QLearning, environment: Environment, num_episodes: int = 1000, steps_per_episode: int = 10):
        """
        Trainer class for training the reinforcement learning agent.
        """
        self.q_learning = q_learning
        self.environment = environment
        self.num_episodes = num_episodes
        self.steps_per_episode = steps_per_episode

    def train(self):
        """
        Runs the training process for the RL agent.
        """
        for episode in range(1, self.num_episodes + 1):
            state = self._get_random_initial_state()

            for _ in range(self.steps_per_episode):
                action = self.q_learning.choose_action(state)
                next_state = self.environment.transition(state, action)
                reward = self.environment.get_reward(
                    state=next_state, action=action)
                self.q_learning.update_q_value(
                    state, action, reward, next_state)
                state = next_state

            if episode % 100 == 0:
                print(f"Episode {episode}/{self.num_episodes} completed.")

        print("Training finished!")
        self.q_learning.save_q_table()  # Save after training

    def evaluate(self, num_trials: int = 10):
        """
        Evaluates the trained policy.
        """
        total_rewards = 0
        for _ in range(num_trials):
            state = self._get_random_initial_state()
            trial_reward = 0

            for _ in range(self.steps_per_episode):
                action = self.q_learning.get_best_action(state)
                state = self.environment.transition(state, action)
                reward = self.environment.get_reward(
                    state=state, action=action)
                trial_reward += reward

            total_rewards += trial_reward

        avg_reward = total_rewards / num_trials
        print(f"Average reward over {num_trials} trials: {avg_reward:.2f}")

    def _get_random_initial_state(self):
        """
        Generates a random initial state for an episode.
        """
        mode = random.choice(list(Mode))
        engagement_level = random.choice(list(EngagementLevel))
        emotional_state = random.choice(list(EmotionalState))

        if mode == Mode.INTERACTION:
            response_quality = random.choice(list(ResponseQuality))
            prompt_necessity = random.choice(list(PromptNecessity))
            response_length = random.choice(list(ResponseLength))
            vocabulary_usage = random.choice(list(VocabularyUsage))
            return State(mode, engagement_level, emotional_state, response_quality, prompt_necessity, response_length, vocabulary_usage)
        else:
            return State(mode, engagement_level, emotional_state)
