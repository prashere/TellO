from enum import Enum

class LexicalType(Enum):
    KNOWN = "Known Vocabulary"
    UNKNOWN = "Unknown Vocabulary"

class SentenceComplexity(Enum):
    SIMPLE = "Simple Sentence"
    MODERATE = "Moderate Sentence"
    COMPLEX = "Complex Sentence"

class ClarificationType(Enum):
    VOCABULARY_EXPLANATION = "Vocabulary Explanation"
    SENTENCE_REPETITION = "Sentence Repetition"
    CONFIRM_CONFUSION = "Confirm Confusion"
    # Confirm confusion is used when the child asks "WHAT" during the interaction,
    # and the robot confirms if a repetition is needed.

class Action:
    def __init__(self, action_type, complexity=None, lexical_type=None, clarification_type=None):
        """
        Initializes an action.
        
        For "Lexical-Syntactic" actions, both complexity and lexical_type must be provided.
        For "Clarification" actions, clarification_type must be provided.
        For "No-Intervention" actions, no additional parameters should be provided.
        
        :param action_type: One of "Lexical-Syntactic", "Clarification", or "No-Intervention".
        :param complexity: (For Lexical-Syntactic) Sentence complexity (Simple, Moderate, Complex).
        :param lexical_type: (For Lexical-Syntactic) Known or Unknown vocabulary.
        :param clarification_type: (For Clarification) Type of clarification (Vocabulary Explanation, Sentence Repetition, or Confirm Confusion).
        """
        if action_type == "Lexical-Syntactic":
            if complexity is None or lexical_type is None:
                raise ValueError("For Lexical-Syntactic actions, both complexity and lexical_type must be provided.")
        elif action_type == "Clarification":
            if clarification_type is None:
                raise ValueError("For Clarification actions, clarification_type must be provided.")
        elif action_type == "No-Intervention":
            if complexity is not None or lexical_type is not None or clarification_type is not None:
                raise ValueError("For No-Intervention actions, no extra parameters should be provided.")
        else:
            raise ValueError("Invalid action_type provided. Choose 'Lexical-Syntactic', 'Clarification', or 'No-Intervention'.")

        self.action_type = action_type
        self.complexity = complexity
        self.lexical_type = lexical_type
        self.clarification_type = clarification_type

    def __repr__(self):
        if self.action_type == "Lexical-Syntactic":
            return f"Action(type={self.action_type}, complexity={self.complexity}, lexical={self.lexical_type})"
        elif self.action_type == "Clarification":
            return f"Action(type={self.action_type}, clarification={self.clarification_type})"
        elif self.action_type == "No-Intervention":
            return f"Action(type={self.action_type})"

    def __eq__(self, other):
        if isinstance(other, Action):
            return (self.action_type == other.action_type and
                    self.complexity == other.complexity and
                    self.lexical_type == other.lexical_type and
                    self.clarification_type == other.clarification_type)
        return False

    def __hash__(self):
        return hash((self.action_type, self.complexity, self.lexical_type, self.clarification_type))

    def to_dict(self):
        return {
            "action_type": self.action_type,
            "complexity": self.complexity.name if self.complexity else None,
            "lexical_type": self.lexical_type.name if self.lexical_type else None,
            "clarification_type": self.clarification_type.name if self.clarification_type else None
        }
