from enum import Enum

class Mode(Enum):
    NARRATION = "Narration Monitoring"
    INTERACTION = "Prompt Interaction"

class Confidence(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

# Prompt necessity means does the child need a prompt again because 
# To the existing one it didn't respond or the engagement wasn't satisfactory
class PromptNecessity(Enum):
    YES = "Yes"
    NO = "No"

class ResponseLength(Enum):
    SHORT = "Short"
    MEDIUM = "Medium"
    LONG = "Long"

class EngagementLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class EmotionalState(Enum):
    HAPPY = "Happy"
    SAD = "Sad"
    EXCITED = "Excited"
    NEUTRAL = "Neutral"
    CONFUSED = "Confused"

class VocabularyUsage(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class ResponseQuality(Enum):
    STRONG = "Strong"    # High confidence & High engagement
    AVERAGE = "Average"  # Medium confidence & engagement
    WEAK = "Weak"        # Low confidence & low engagement

class State:
    def __init__(
        self, 
        mode: Mode,
        engagement_level: EngagementLevel,
        emotional_state: EmotionalState,
        response_quality: ResponseQuality = None, 
        prompt_necessity: PromptNecessity = None, 
        response_length: ResponseLength = None, 
        vocabulary_usage: VocabularyUsage = None
    ):
        """
        Initializes the state with attributes that depend on the mode.

        :param mode: The phase the robot is in (Narration Monitoring or Prompt Interaction).
        :param engagement_level: How engaged the child is.
        :param emotional_state: The child's emotional state.
        
        Only used in INTERACTION mode:
        :param response_quality: A combined metric for engagement & confidence.
        :param prompt_necessity: Whether the child required a prompt.
        :param response_length: The length of the child's response.
        :param vocabulary_usage: Categorized count of known words used by the child.
        """
        self.mode = mode
        self.engagement_level = engagement_level
        self.emotional_state = emotional_state
        
        # Only relevant for INTERACTION mode
        self.response_quality = response_quality if mode == Mode.INTERACTION else None
        self.prompt_necessity = prompt_necessity if mode == Mode.INTERACTION else None
        self.response_length = response_length if mode == Mode.INTERACTION else None
        self.vocabulary_usage = vocabulary_usage if mode == Mode.INTERACTION else None

    def __repr__(self):
        base = f"State(mode={self.mode.value}, engagement_level={self.engagement_level.value}, emotional_state={self.emotional_state.value}"
        if self.mode == Mode.INTERACTION:
            base += (f", response_quality={self.response_quality.value}, prompt_necessity={self.prompt_necessity.value}, "
                     f"response_length={self.response_length.value}, vocabulary_usage={self.vocabulary_usage.value}")
        return base + ")"

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.mode == other.mode and
                self.engagement_level == other.engagement_level and
                self.emotional_state == other.emotional_state and
                self.response_quality == other.response_quality and
                self.prompt_necessity == other.prompt_necessity and
                self.response_length == other.response_length and
                self.vocabulary_usage == other.vocabulary_usage)

    def __hash__(self):
        return hash((self.mode, self.engagement_level, self.emotional_state, 
                     self.response_quality, self.prompt_necessity, self.response_length, self.vocabulary_usage))

    def to_tuple(self):
        """
        Returns a tuple representation of the state for use as a dictionary key.
        """
        base = (self.mode.value, self.engagement_level.value, self.emotional_state.value)
        if self.mode == Mode.INTERACTION:
            return base + (self.response_quality.value, self.prompt_necessity.value, 
                           self.response_length.value, self.vocabulary_usage.value)
        return base


# Child is listening during narration
# state_narration = State(
#     mode=Mode.NARRATION,
#     engagement_level=EngagementLevel.HIGH,
#     emotional_state=EmotionalState.HAPPY
# )

# Child is responding after a prompt
# state_interaction = State(
#     mode=Mode.INTERACTION,
#     engagement_level=EngagementLevel.MEDIUM,
#     emotional_state=EmotionalState.CONFUSED,
#     response_quality=ResponseQuality.WEAK,
#     prompt_necessity=PromptNecessity.YES,
#     response_length=ResponseLength.SHORT,
#     vocabulary_usage=VocabularyUsage.LOW
# )

# print(state_narration.to_tuple())
# print(state_interaction.to_tuple())
