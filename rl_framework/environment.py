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

        # Learning score based on vocabulary usage level
        learning_score = {
            VocabularyUsage.LOW: 0.0,
            VocabularyUsage.MEDIUM: 0.5,
            VocabularyUsage.HIGH: 1.0
        }[state.vocabulary_usage] if state.mode == Mode.INTERACTION else 0  # Only applies in INTERACTION mode

        return 0.5 * engagement_score + 0.5 * learning_score

    def transition(self, state: State, action: Action) -> State:
        """
        Simulates the state transition after an action.
        :param state: The current state.
        :param action: The action taken.
        :return: The next state.
        """
        new_engagement_level = random.choice(list(EngagementLevel))
        new_emotional_state = random.choice(list(EmotionalState))

        if state.mode == Mode.NARRATION:
            # No speech-related changes in narration mode
            return State(
                mode=Mode.NARRATION,
                engagement_level=new_engagement_level,
                emotional_state=new_emotional_state
            )

        else:  # Mode.INTERACTION
            new_response_quality = random.choice(list(ResponseQuality))
            new_prompt_necessity = random.choice(list(PromptNecessity))
            new_response_length = random.choice(list(ResponseLength))

            # Adjust vocabulary usage based on action
            if action.lexical_type == LexicalType.KNOWN:
                new_vocab_usage = VocabularyUsage.HIGH if state.vocabulary_usage == VocabularyUsage.MEDIUM else VocabularyUsage.MEDIUM
            else:
                new_vocab_usage = VocabularyUsage.LOW if state.vocabulary_usage == VocabularyUsage.MEDIUM else VocabularyUsage.MEDIUM

            return State(
                mode=Mode.INTERACTION,
                engagement_level=new_engagement_level,
                emotional_state=new_emotional_state,
                response_quality=new_response_quality,
                prompt_necessity=new_prompt_necessity,
                response_length=new_response_length,
                vocabulary_usage=new_vocab_usage
            )

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
            print()

# Example Usage:
q_learning_agent = QLearning(actions)
env = Environment(q_learning_agent)

# Define an initial state for narration (listening mode)
initial_state_narration = State(
    mode=Mode.NARRATION,
    engagement_level=EngagementLevel.HIGH,
    emotional_state=EmotionalState.HAPPY
)

# Define an initial state for interaction (responding mode)
initial_state_interaction = State(
    mode=Mode.INTERACTION,
    engagement_level=EngagementLevel.MEDIUM,
    emotional_state=EmotionalState.NEUTRAL,
    response_quality=ResponseQuality.AVERAGE,
    prompt_necessity=PromptNecessity.NO,
    response_length=ResponseLength.MEDIUM,
    vocabulary_usage=VocabularyUsage.MEDIUM
)

print("\n--- Running Narration Mode Episode ---\n")
env.run_episode(initial_state_narration)

print("\n--- Running Interaction Mode Episode ---\n")
env.run_episode(initial_state_interaction)
