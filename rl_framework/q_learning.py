import random
from typing import List
from state import State, Mode, EngagementLevel, EmotionalState, ResponseQuality, PromptNecessity, ResponseLength, VocabularyUsage
from actions import Action, SentenceComplexity, LexicalType, ClarificationType


class QLearning:
    def __init__(self, actions: List[Action], alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.2):
        """
        Initializes the Q-learning agent.
        
        :param actions: List of all possible actions.
        :param alpha: Learning rate.
        :param gamma: Discount factor.
        :param epsilon: Exploration rate (ϵ-greedy strategy).
        """
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = {}  # Q-table mapping from state tuple to list of Q-values

    def _get_q_values(self, state: State) -> List[float]:
        """
        Returns the list of Q-values for the given state.
        If the state is not yet in the Q-table, initializes Q-values to 0.
        
        :param state: Current state.
        :return: List of Q-values for each action.
        """
        state_key = state.to_tuple()
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0 for _ in self.actions]
        return self.q_table[state_key]

    def choose_action(self, state: State) -> Action:
        """
        Chooses an action using an epsilon-greedy strategy.
        
        :param state: The current state.
        :return: The selected Action.
        """
        q_values = self._get_q_values(state)
        if random.random() < self.epsilon:
            # Exploration: Choose a random action.
            return random.choice(self.actions)
        else:
            # Exploitation: Choose the action with the highest Q-value.
            max_q = max(q_values)
            best_actions = [action for action, q in zip(self.actions, q_values) if q == max_q]
            return random.choice(best_actions)

    def update_q_value(self, state: State, action: Action, reward: float, next_state: State) -> None:
        """
        Updates the Q-value for a state-action pair using the Q-learning update rule.
        
        :param state: The current state.
        :param action: The action taken.
        :param reward: The reward received after taking the action.
        :param next_state: The next state resulting from the action.
        """
        state_key = state.to_tuple()
        action_index = self.actions.index(action)
        
        current_q = self._get_q_values(state)[action_index]
        max_next_q = max(self._get_q_values(next_state))
        
        # Q-learning update rule:
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state_key][action_index] = new_q

    def get_best_action(self, state: State) -> Action:
        """
        Retrieves the best action (the one with the highest Q-value) for a given state.
        
        :param state: The current state.
        :return: The best Action.
        """
        q_values = self._get_q_values(state)
        max_q = max(q_values)
        best_actions = [action for action, q in zip(self.actions, q_values) if q == max_q]
        return random.choice(best_actions)

# # Define possible actions
# actions = [
#     Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.SIMPLE, lexical_type=LexicalType.KNOWN),
#     Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.MODERATE, lexical_type=LexicalType.UNKNOWN),
#     Action(action_type="Clarification", clarification_type=ClarificationType.VOCABULARY_EXPLANATION),
#     Action(action_type="Clarification", clarification_type=ClarificationType.SENTENCE_REPETITION),
# ]

# # Initialize Q-learning agent with the action space
# agent = QLearning(actions=actions, alpha=0.1, gamma=0.9, epsilon=0.2)

# # Define an initial state in Narration Mode
# state_narration = State(
#     mode=Mode.NARRATION,
#     engagement_level=EngagementLevel.MEDIUM,
#     emotional_state=EmotionalState.HAPPY
# )

# # Define an interaction state (after a prompt)
# state_interaction = State(
#     mode=Mode.INTERACTION,
#     engagement_level=EngagementLevel.LOW,
#     emotional_state=EmotionalState.SAD,
#     response_quality=ResponseQuality.WEAK,
#     prompt_necessity=PromptNecessity.YES,
#     response_length=ResponseLength.SHORT,
#     vocabulary_usage=VocabularyUsage.LOW
# )

# # Step 1: Choose an action based on the initial state
# chosen_action = agent.choose_action(state_interaction)
# print(f"Chosen Action: {chosen_action}")

# # Step 2: Simulate receiving a reward for this action
# simulated_reward = 1.0  # Example reward

# # Step 3: Transition to a new state after applying the action
# next_state = State(
#     mode=Mode.INTERACTION,
#     engagement_level=EngagementLevel.MEDIUM,  # Engagement improved
#     emotional_state=EmotionalState.NEUTRAL,  # Child became neutral after interaction
#     response_quality=ResponseQuality.AVERAGE,
#     prompt_necessity=PromptNecessity.NO,  # No further prompt needed
#     response_length=ResponseLength.MEDIUM,
#     vocabulary_usage=VocabularyUsage.MEDIUM
# )

# # Step 4: Update Q-value based on experience
# agent.update_q_value(state_interaction, chosen_action, simulated_reward, next_state)

# # Step 5: Retrieve updated Q-values for verification
# updated_q_values = agent._get_q_values(state_interaction)
# print(f"Updated Q-Values: {updated_q_values}")

# # Step 6: Retrieve the best action for the next state
# best_action = agent.get_best_action(next_state)
# print(f"Best action for next state: {best_action}")
