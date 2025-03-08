from enum import Enum

class Confidence(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

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
    # Add other states as necessary

class State:
    def __init__(self, confidence: Confidence, prompt_necessity: PromptNecessity, response_length: ResponseLength, vocabulary_usage: int, engagement_level: EngagementLevel, emotional_state: EmotionalState):
        """
        Initializes the state with task-related details and affective details.
        :param confidence: Confidence level of the child's response.
        :param prompt_necessity: Whether the child required a prompt.
        :param response_length: The length of the child's response.
        :param vocabulary_usage: Count of known words used by the child.
        :param engagement_level: How engaged the child is.
        :param emotional_state: The child's emotional state.
        """
        self.confidence = confidence
        self.prompt_necessity = prompt_necessity
        self.response_length = response_length
        self.vocabulary_usage = vocabulary_usage
        self.engagement_level = engagement_level
        self.emotional_state = emotional_state

    def __repr__(self):
        return (f"State(confidence={self.confidence.value}, prompt_necessity={self.prompt_necessity.value}, "
                f"response_length={self.response_length.value}, vocabulary_usage={self.vocabulary_usage}, "
                f"engagement_level={self.engagement_level.value}, emotional_state={self.emotional_state.value})")

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.confidence == other.confidence and
                self.prompt_necessity == other.prompt_necessity and
                self.response_length == other.response_length and
                self.vocabulary_usage == other.vocabulary_usage and
                self.engagement_level == other.engagement_level and
                self.emotional_state == other.emotional_state)

    def __hash__(self):
        return hash((self.confidence, self.prompt_necessity, self.response_length, 
                     self.vocabulary_usage, self.engagement_level, self.emotional_state))

    def to_tuple(self):
        """
        Returns a tuple representation of the state for use as a dictionary key.
        """
        return (self.confidence.value, self.prompt_necessity.value, self.response_length.value, 
                self.vocabulary_usage, self.engagement_level.value, self.emotional_state.value)

# # Usage example
# current_state = State(
#     confidence=Confidence.HIGH,
#     prompt_necessity=PromptNecessity.NO,
#     response_length=ResponseLength.LONG,
#     vocabulary_usage=3,
#     engagement_level=EngagementLevel.HIGH,
#     emotional_state=EmotionalState.HAPPY
# )

# print(current_state)
# print(current_state.to_tuple())
