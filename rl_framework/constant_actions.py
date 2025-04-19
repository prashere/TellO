from .actions import Action, SentenceComplexity, LexicalType, ClarificationType

lexical_syntactic_actions = [
    Action(action_type="Lexical-Syntactic",
           complexity=SentenceComplexity.SIMPLE, lexical_type=LexicalType.KNOWN),
    Action(action_type="Lexical-Syntactic",
           complexity=SentenceComplexity.SIMPLE, lexical_type=LexicalType.UNKNOWN),
    Action(action_type="Lexical-Syntactic",
           complexity=SentenceComplexity.MODERATE, lexical_type=LexicalType.KNOWN),
    Action(action_type="Lexical-Syntactic",
           complexity=SentenceComplexity.MODERATE, lexical_type=LexicalType.UNKNOWN),
    Action(action_type="Lexical-Syntactic",
           complexity=SentenceComplexity.COMPLEX, lexical_type=LexicalType.KNOWN),
    Action(action_type="Lexical-Syntactic",
           complexity=SentenceComplexity.COMPLEX, lexical_type=LexicalType.UNKNOWN),
]

clarification_actions = [
    Action(action_type="Clarification",
           clarification_type=ClarificationType.VOCABULARY_EXPLANATION),
    Action(action_type="Clarification",
           clarification_type=ClarificationType.SENTENCE_REPETITION),
    Action(action_type="Clarification",
           clarification_type=ClarificationType.CONFIRM_CONFUSION),
]

no_intervention_actions = [
    Action(action_type="No-Intervention")
]

all_actions = lexical_syntactic_actions + \
    clarification_actions + no_intervention_actions


def get_all_actions():
    return all_actions



