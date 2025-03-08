import random
from typing import List
from actions import *
from state import *


class QLearning:
    def __init__(self, actions: List[Action], alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.2):
        """
        Initializes the Q-learning agent.
        :param actions: List of all possible actions.
        :param alpha: Learning rate.
        :param gamma: Discount factor.
        :param epsilon: Exploration rate for ϵ-greedy strategy.
        """
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}  # Q-table to store Q-values (state -> [Q-values for actions])

    def _get_q_values(self, state: State):
        """Returns the Q-values for the given state. Initializes if not yet encountered."""
        state_tuple = state.to_tuple()
        if state_tuple not in self.q_table:
            # Initialize Q-values for all actions to 0
            self.q_table[state_tuple] = [0.0] * len(self.actions)
        return self.q_table[state_tuple]

    def choose_action(self, state: State):
        """
        Chooses an action using the ϵ-greedy policy.
        :param state: The current state of the system.
        :return: The selected action.
        """
        q_values = self._get_q_values(state)
        
        # Exploration vs. Exploitation
        if random.random() < self.epsilon:
            # Exploration: Choose a random action
            action = random.choice(self.actions)
        else:
            # Exploitation: Choose the action with the highest Q-value
            max_q_value = max(q_values)
            best_actions = [a for a, q in zip(self.actions, q_values) if q == max_q_value]
            action = random.choice(best_actions)  # In case of ties, pick randomly
        
        return action

    def update_q_value(self, state: State, action: Action, reward: float, next_state: State):
        """
        Updates the Q-value for a given state-action pair using the Q-learning update rule.
        :param state: The current state.
        :param action: The action taken.
        :param reward: The reward received after taking the action.
        :param next_state: The next state after taking the action.
        """
        state_tuple = state.to_tuple()
        action_index = self.actions.index(action)
        
        # Get the current Q-value for the state-action pair
        current_q_value = self._get_q_values(state)[action_index]

        # Get the maximum Q-value for the next state
        next_q_values = self._get_q_values(next_state)
        max_next_q_value = max(next_q_values)

        # Q-learning formula: Update the Q-value
        updated_q_value = current_q_value + self.alpha * (reward + self.gamma * max_next_q_value - current_q_value)

        # Update the Q-table
        self.q_table[state_tuple][action_index] = updated_q_value

    def get_best_action(self, state: State):
        """
        Get the action with the highest Q-value for a given state.
        :param state: The current state.
        :return: The best action for the state.
        """
        q_values = self._get_q_values(state)
        max_q_value = max(q_values)
        best_actions = [a for a, q in zip(self.actions, q_values) if q == max_q_value]
        return random.choice(best_actions)  # In case of ties, pick randomly

# Example Usage:
# Define some actions for the robot (as you defined before)
# Lexical-Syntactic Actions:
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


# Create the Q-learning agent
q_learning_agent = QLearning(actions)

# Simulate a scenario where we have some states
# Child is responding after a prompt (Interaction Mode)
state = State(
    mode=Mode.INTERACTION,
    engagement_level=EngagementLevel.HIGH,
    emotional_state=EmotionalState.HAPPY,
    response_quality=ResponseQuality.STRONG,
    prompt_necessity=PromptNecessity.NO,
    response_length=ResponseLength.LONG,
    vocabulary_usage=VocabularyUsage.HIGH
)

# Child is listening to the robot's narration (Narration Mode)
next_state = State(
    mode=Mode.NARRATION,
    engagement_level=EngagementLevel.MEDIUM,
    emotional_state=EmotionalState.SAD
)


# Choose an action
action = q_learning_agent.choose_action(state)
# print("\n")
# print(f"Chosen Action: {action}")
# print("\n")

# # Simulate reward and update Q-value
# reward = 1.0  # Example reward
# q_learning_agent.update_q_value(state, action, reward, next_state)

# # Get the best action after the update
# best_action = q_learning_agent.get_best_action(state)
# print(f"Best Action after Update: {best_action}")
# print("\n")

