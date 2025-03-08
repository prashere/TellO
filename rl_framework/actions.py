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
    # Basically confirm confusion is something like when the child asks "WHAT" in the middle
    # You confirm that by asking "Do you want me to repeat ?"
    # or something similar

class Action:
    def __init__(self, action_type, complexity=None, lexical_type=None, clarification_type=None):
        if action_type == "Lexical-Syntactic":
            if complexity is None or lexical_type is None:
                raise ValueError("For Lexical-Syntactic actions, both complexity and lexical_type must be provided.")
        elif action_type == "Clarification":
            if clarification_type is None:
                raise ValueError("For Clarification actions, clarification_type must be provided.")
        
        self.action_type = action_type
        self.complexity = complexity
        self.lexical_type = lexical_type
        self.clarification_type = clarification_type

    def __repr__(self):
        if self.action_type == "Lexical-Syntactic":
            return f"Action(type={self.action_type}, complexity={self.complexity}, lexical={self.lexical_type})"
        elif self.action_type == "Clarification":
            return f"Action(type={self.action_type}, clarification={self.clarification_type})"

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


# Example Usage

# # Lexical-Syntactic Action:
# action_1 = Action(action_type="Lexical-Syntactic", complexity=SentenceComplexity.SIMPLE, lexical_type=LexicalType.KNOWN)

# # Clarification Action:
# action_2 = Action(action_type="Clarification", clarification_type=ClarificationType.VOCABULARY_EXPLANATION)

# print(action_1)
# print(action_2)
# print(action_1 == action_2)

# # Convert action to dictionary
# print(action_1.to_dict())
# print(action_2.to_dict())
