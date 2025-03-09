import random
import os
import pickle
from environment import Environment
from q_learning import QLearning
from state import State, Mode, EngagementLevel, EmotionalState, ResponseQuality, PromptNecessity, ResponseLength, VocabularyUsage
from actions import Action, SentenceComplexity, LexicalType, ClarificationType

class Trainer:
    def __init__(self, q_learning: QLearning, environment: Environment, num_episodes: int = 1000, steps_per_episode: int = 10):
        """
        Trainer class for training the reinforcement learning agent.

        :param q_learning: The Q-learning agent.
        :param environment: The environment to interact with.
        :param num_episodes: Number of training episodes.
        :param steps_per_episode: Steps per episode.
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
            # Start with a random initial state
            initial_state = self._get_random_initial_state()
            state = initial_state

            for _ in range(self.steps_per_episode):
                action = self.q_learning.choose_action(state)
                next_state = self.environment.transition(state, action)
                reward = self.environment.get_reward(next_state)

                self.q_learning.update_q_value(state, action, reward, next_state)
                state = next_state  # Move to the next state

            if episode % 100 == 0:
                print(f"Episode {episode}/{self.num_episodes} completed.")

        print("Training finished!")

    def evaluate(self, num_trials: int = 10):
        """
        Evaluates the trained policy.
        :param num_trials: Number of test trials.
        """
        total_rewards = 0

        for _ in range(num_trials):
            state = self._get_random_initial_state()
            trial_reward = 0

            for _ in range(self.steps_per_episode):
                action = self.q_learning.get_best_action(state)
                state = self.environment.transition(state, action)
                reward = self.environment.get_reward(state)
                trial_reward += reward

            total_rewards += trial_reward

        avg_reward = total_rewards / num_trials
        print(f"Average reward over {num_trials} trials: {avg_reward:.2f}")

    def save_q_table(self, filename="q_table.pkl"):
        """
        Saves the Q-table to a file.
        """
        filename = "./rl_framework/table/" + filename
        os.makedirs('./rl_framework/table', exist_ok=True)
        with open(filename, "wb") as file:
            pickle.dump(self.q_learning.q_table, file)
        print(f"Q-table saved to {filename}")

    def load_q_table(self, filename="q_table.pkl"):
        """
        Loads the Q-table from a file.
        """
        try:
            filename = "./rl_framework/table/" + filename
            with open(filename, "rb") as file:
                self.q_learning.q_table = pickle.load(file)
            print(f"Q-table loaded from {filename}")
        except FileNotFoundError:
            print("No saved Q-table found. Starting fresh.")

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

# Example usage
if __name__ == "__main__":
    action_1 = Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.SIMPLE, lexical_type=LexicalType.KNOWN)
    action_2 = Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.SIMPLE, lexical_type=LexicalType.UNKNOWN)
    action_3 = Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.MODERATE, lexical_type=LexicalType.KNOWN)
    action_4 = Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.MODERATE, lexical_type=LexicalType.UNKNOWN)
    action_5 = Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.COMPLEX, lexical_type=LexicalType.KNOWN)
    action_6 = Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.COMPLEX, lexical_type=LexicalType.UNKNOWN)

    # Clarification Actions:
    action_7 = Action(action_type="Clarification", clarification_type=ClarificationType.VOCABULARY_EXPLANATION)
    action_8 = Action(action_type="Clarification", clarification_type=ClarificationType.SENTENCE_REPETITION)
    action_9 = Action(action_type="Clarification", clarification_type=ClarificationType.CONFIRM_CONFUSION)

    # Actions list
    actions = [action_1, 
           action_2, 
           action_3, 
           action_4, 
           action_5, 
           action_6, 
           action_7, 
           action_8, 
           action_9]

    # Create Q-learning agent and environment
    q_learning_agent = QLearning(actions)  # 'actions' list comes from actions.py
    env = Environment(q_learning_agent)

    # Create and train the trainer
    trainer = Trainer(q_learning_agent, env)

    # trainer.load_q_table()
    # If I want to use the previous training knowledge I need to activate the above line

    trainer.train()

    # Evaluate trained model
    trainer.evaluate()

    # Save trained Q-table
    trainer.save_q_table()
