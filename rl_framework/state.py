from enum import Enum

class Mode(Enum):
    NARRATION = "Narration Monitoring"
    INTERACTION = "Prompt Interaction"

class Confidence(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

# Prompt necessity means whether the child needs a prompt again 
# because the existing one didn't yield a satisfactory response.
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
    SURPRISE = "Surprise"
    NEUTRAL = "Neutral"
    FEAR = "Fear"
    DISGUST = "Disgust"
    ANGER = "Anger"

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
        vocabulary_usage: VocabularyUsage = None,
        wh_question_detected: bool = False  # New attribute to indicate if a WH-question is detected
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
        :param wh_question_detected: True if the child's response includes a WH-question, triggering clarification.
        """
        self.mode = mode
        self.engagement_level = engagement_level
        self.emotional_state = emotional_state
        
        # Only relevant for INTERACTION mode
        self.response_quality = response_quality if mode == Mode.INTERACTION else None
        self.prompt_necessity = prompt_necessity if mode == Mode.INTERACTION else None
        self.response_length = response_length if mode == Mode.INTERACTION else None
        self.vocabulary_usage = vocabulary_usage if mode == Mode.INTERACTION else None
        self.wh_question_detected = wh_question_detected if mode == Mode.INTERACTION else False

    def __repr__(self):
        base = f"State(mode={self.mode.value}, engagement_level={self.engagement_level.value}, emotional_state={self.emotional_state.value}"
        if self.mode == Mode.INTERACTION:
            base += (f", response_quality={self.response_quality.value}, prompt_necessity={self.prompt_necessity.value}, "
                     f"response_length={self.response_length.value}, vocabulary_usage={self.vocabulary_usage.value}, "
                     f"wh_question_detected={self.wh_question_detected})")
        else:
            base += ")"
        return base

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        return (self.mode == other.mode and
                self.engagement_level == other.engagement_level and
                self.emotional_state == other.emotional_state and
                self.response_quality == other.response_quality and
                self.prompt_necessity == other.prompt_necessity and
                self.response_length == other.response_length and
                self.vocabulary_usage == other.vocabulary_usage and
                self.wh_question_detected == other.wh_question_detected)

    def __hash__(self):
        return hash((self.mode, self.engagement_level, self.emotional_state, 
                     self.response_quality, self.prompt_necessity, self.response_length, 
                     self.vocabulary_usage, self.wh_question_detected))

    def to_tuple(self):
        """
        Returns a tuple representation of the state for use as a dictionary key.
        """
        base = (self.mode.value, self.engagement_level.value, self.emotional_state.value)
        if self.mode == Mode.INTERACTION:
            return base + (self.response_quality.value, self.prompt_necessity.value, 
                           self.response_length.value, self.vocabulary_usage.value, 
                           self.wh_question_detected)
        return base


# def test_state_emotion_engagement_update():
#     print("Running Test 15: State object updates...")

#     # Simulate 1: High engagement + Happy emotion in Narration Mode
#     state1 = State(
#         mode=Mode.NARRATION,
#         engagement_level=EngagementLevel.HIGH,
#         emotional_state=EmotionalState.HAPPY
#     )
#     assert state1.mode == Mode.NARRATION
#     assert state1.engagement_level == EngagementLevel.HIGH
#     assert state1.emotional_state == EmotionalState.HAPPY
#     print("✔ State 1 passed.")

#     # Simulate 2: Low engagement + Sad emotion in Interaction Mode with weak response
#     state2 = State(
#         mode=Mode.INTERACTION,
#         engagement_level=EngagementLevel.LOW,
#         emotional_state=EmotionalState.SAD,
#         response_quality=ResponseQuality.WEAK,
#         prompt_necessity=PromptNecessity.YES,
#         response_length=ResponseLength.SHORT,
#         vocabulary_usage=VocabularyUsage.LOW,
#         wh_question_detected=False
#     )
#     assert state2.mode == Mode.INTERACTION
#     assert state2.engagement_level == EngagementLevel.LOW
#     assert state2.emotional_state == EmotionalState.SAD
#     assert state2.response_quality == ResponseQuality.WEAK
#     assert state2.prompt_necessity == PromptNecessity.YES
#     assert state2.response_length == ResponseLength.SHORT
#     assert state2.vocabulary_usage == VocabularyUsage.LOW
#     assert not state2.wh_question_detected
#     print("✔ State 2 passed.")

#     # Simulate 3: Medium engagement + Surprise emotion with WH question
#     state3 = State(
#         mode=Mode.INTERACTION,
#         engagement_level=EngagementLevel.MEDIUM,
#         emotional_state=EmotionalState.SURPRISE,
#         response_quality=ResponseQuality.AVERAGE,
#         prompt_necessity=PromptNecessity.NO,
#         response_length=ResponseLength.MEDIUM,
#         vocabulary_usage=VocabularyUsage.MEDIUM,
#         wh_question_detected=True
#     )
#     assert state3.wh_question_detected is True
#     assert state3.response_quality == ResponseQuality.AVERAGE
#     print("✔ State 3 passed.")

#     print("✅ Test 15 Passed: Agent state reflects emotional and engagement changes correctly.\n")

# # Run the test
# test_state_emotion_engagement_update()
