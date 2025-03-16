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

    def reset(self):
        """Reset the environment and return an initial state for a new episode."""
        initial_state = State(
            mode=Mode.NARRATION,  # Start in narration mode
            engagement_level=EngagementLevel.MEDIUM,  # Neutral starting point
            emotional_state=EmotionalState.NEUTRAL,  # Assume no strong emotion initially
            response_quality=ResponseQuality.AVERAGE,
            prompt_necessity=PromptNecessity.NO,
            response_length=ResponseLength.MEDIUM,
            vocabulary_usage=VocabularyUsage.MEDIUM,
            wh_question_detected=False
        )
        return initial_state

    def get_reward(self, state: State, action: Action) -> float:
        """
        Computes a reward based on the engagement and learning progress, while considering emotional state and prompts.
        :param state: The current state.
        :param action: The action taken.
        :return: A reward value.
        """
        # Engagement score: High, Medium, Low
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

        # Emotional state consideration
        emotional_penalty = 0
        if state.emotional_state == EmotionalState.ANGER:
            # Penalty if the child is angry (because frustration may rise with complexity)
            emotional_penalty = -0.2
        elif state.emotional_state == EmotionalState.SURPRISE:
            # Mild penalty for surprise (suggests confusion)
            emotional_penalty = -0.1

        # Penalty if a prompt is needed too frequently when engagement is low
        prompt_penalty = -0.2 if state.prompt_necessity == PromptNecessity.YES and state.engagement_level == EngagementLevel.LOW else 0

        # Clarification reward/penalty based on the action
        clarification_bonus = 0
        if action.action_type == "Clarification":
            if state.engagement_level == EngagementLevel.LOW:
                clarification_bonus = 0.5  # Reward if clarification helps in low engagement situations
            else:
                # Penalize if clarification is used when engagement is high (over-prompting)
                clarification_bonus = -0.3

        # Combining all factors: Engagement + Learning + Emotional + Clarification + Prompt
        total_reward = 0.5 * engagement_score + 0.5 * learning_score + \
            emotional_penalty + clarification_bonus + prompt_penalty

        # Ensure rewards stay within reasonable bounds
        total_reward = max(-1.0, min(1.0, total_reward))

        return total_reward

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
            # In narration mode, only update engagement and emotion.
            return State(
                mode=Mode.NARRATION,
                engagement_level=new_engagement_level,
                emotional_state=new_emotional_state
            )
        else:  # INTERACTION mode
            new_response_quality = random.choice(list(ResponseQuality))
            new_prompt_necessity = random.choice(list(PromptNecessity))
            new_response_length = random.choice(list(ResponseLength))

            # Probabilistic update of vocabulary_usage based on action's lexical type
            if action.action_type == "Lexical-Syntactic":
                rand = random.random()

                # Introduce bias towards LOW vocabulary usage, especially early on
                if state.vocabulary_usage == VocabularyUsage.LOW:
                    if rand < 0.7:
                        new_vocab_usage = VocabularyUsage.LOW
                    else:
                        new_vocab_usage = VocabularyUsage.MEDIUM
                elif state.vocabulary_usage == VocabularyUsage.MEDIUM:
                    if rand < 0.4:
                        new_vocab_usage = VocabularyUsage.MEDIUM
                    elif 0.4 < rand < 0.7:
                        new_vocab_usage = VocabularyUsage.LOW
                    else:
                        new_vocab_usage = VocabularyUsage.HIGH

                else:  # HIGH vocabulary usage
                    if rand < 0.7:
                        new_vocab_usage = VocabularyUsage.HIGH
                    else:
                        new_vocab_usage = VocabularyUsage.MEDIUM
            else:
                new_vocab_usage = state.vocabulary_usage

            # Simulate WH-question detection (in practice, this is derived from analyzing the child's speech)
            new_wh_question = random.choice([True, False])

            return State(
                mode=Mode.INTERACTION,
                engagement_level=new_engagement_level,
                emotional_state=new_emotional_state,
                response_quality=new_response_quality,
                prompt_necessity=new_prompt_necessity,
                response_length=new_response_length,
                vocabulary_usage=new_vocab_usage,
                wh_question_detected=new_wh_question
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
            reward = self.get_reward(state, action)
            self.q_learning.update_q_value(state, action, reward, next_state)
            state = next_state
            print(f"Action: {action}, Reward: {reward}, New State: {state}")
            print()


# Example initialization of the Q-learning agent
actions = [Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.SIMPLE, lexical_type=LexicalType.KNOWN),
           Action(action_type="Clarification", clarification_type=ClarificationType.SENTENCE_REPETITION)]

q_learning_agent = QLearning(actions)

# Initialize the environment with the Q-learning agent
env = Environment(q_learning_agent)

# Define initial state for INTERACTION mode (simulating a real interaction scenario)
initial_state = State(
    mode=Mode.INTERACTION,
    engagement_level=EngagementLevel.MEDIUM,
    emotional_state=EmotionalState.HAPPY,
    response_quality=ResponseQuality.AVERAGE,
    # Example scenario where a prompt is needed
    prompt_necessity=PromptNecessity.YES,
    response_length=ResponseLength.MEDIUM,
    vocabulary_usage=VocabularyUsage.MEDIUM
)

# Run an episode of interaction in the environment
print("\n--- Running Interaction Mode Episode ---\n")
# You can adjust num_steps as needed
env.run_episode(initial_state, num_steps=5)

# Running multiple episodes could help observe how the system adapts over time with rewards and state transitions
