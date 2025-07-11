import time
from collections import deque, Counter
import statistics
from rl_framework.state import Mode, EngagementLevel, EmotionalState, ResponseQuality, PromptNecessity, ResponseLength, VocabularyUsage, State

HEAD_POSE_MAPPING = {
    "Front": 0,
    "Left": 1,
    "Right": 2,
    "Up": 3,
    "Down": 4
}
GAZE_MAPPING = {
    "Looking left": 1,
    "Looking right": 2,
    "Looking center": 0,
    "Blinking": 3
}
EMOTION_MAPPING = {
    "Angry": 0,
    "Disgust": 1,
    "Fear": 2,
    "Happy": 3,
    "Neutral": 4,
    "Sad": 5,
    "Surprise": 6
}


class StateUpdater:
    def __init__(self, update_interval=60):
        # Buffers to store sensor outputs during the window
        self.head_horizontal_buffer = deque(maxlen=100)
        self.head_vertical_buffer = deque(maxlen=100)
        self.gaze_buffer = deque(maxlen=100)
        self.emotion_buffer = deque(maxlen=100)
        self.emotion_conf_buffer = deque(maxlen=100)

        self.last_update_time = time.time()
        self.update_interval = update_interval  # seconds

        self.current_state = None

    def add_reading(self, horizontal, vertical, gaze, emotion, emotion_conf):
        try:
            self.head_horizontal_buffer.append(horizontal)
            self.head_vertical_buffer.append(vertical)
            self.gaze_buffer.append(gaze)
            self.emotion_buffer.append(emotion)
            self.emotion_conf_buffer.append(emotion_conf)
        except Exception as e:
            print("Error in add_reading:", e)

    def aggregate_head_pose(self):
        try:
            horizontal_values = [HEAD_POSE_MAPPING[pose]
                                 for pose in self.head_horizontal_buffer if pose in HEAD_POSE_MAPPING]
            vertical_values = [HEAD_POSE_MAPPING[pose]
                               for pose in self.head_vertical_buffer if pose in HEAD_POSE_MAPPING]
            horizontal_mode = Counter(horizontal_values).most_common(
                1)[0][0] if horizontal_values else HEAD_POSE_MAPPING["Front"]
            vertical_mode = Counter(vertical_values).most_common(
                1)[0][0] if vertical_values else HEAD_POSE_MAPPING["Front"]
            return horizontal_mode, vertical_mode
        except Exception as e:
            print("Error in aggregate_head_pose:", e)
            return HEAD_POSE_MAPPING["Front"], HEAD_POSE_MAPPING["Front"]

    def aggregate_gaze(self):
        try:
            if self.gaze_buffer:
                gaze_mode = Counter(self.gaze_buffer).most_common(1)[0][0]
                return GAZE_MAPPING.get(gaze_mode, 0)
            else:
                return 0
        except Exception as e:
            print("Error in aggregate_gaze:", e)
            return 0

    def aggregate_emotion(self):
        try:
            if not self.emotion_buffer:
                return 4, 0.0  # Neutral and 0.0 confidence
            counts = Counter(self.emotion_buffer)
            most_common_emotion, _ = counts.most_common(1)[0]
            # Filter out any None values from confidence
            confs = [conf for emo, conf in zip(
                self.emotion_buffer, self.emotion_conf_buffer) if emo == most_common_emotion and conf is not None]
            avg_conf = statistics.mean(confs) if confs else 0.0
            return EMOTION_MAPPING.get(most_common_emotion, 4), avg_conf
        except Exception as e:
            print("Error in aggregate_emotion:", e)
            return 4, 0.0

    def update_state(self):
        try:
            horizontal, vertical = self.aggregate_head_pose()
            gaze = self.aggregate_gaze()
            emotion_idx, emotion_conf = self.aggregate_emotion()
        except Exception as e:
            print("Error during state aggregation:", e)
            horizontal, vertical, gaze, emotion_idx, emotion_conf = HEAD_POSE_MAPPING[
                "Front"], HEAD_POSE_MAPPING["Front"], 0, 4, 0.0

        try:
            emotion_list = list(EMOTION_MAPPING.keys())
            emotion_name = emotion_list[emotion_idx] if emotion_idx in range(
                len(emotion_list)) else "Neutral"
            emotional_state = getattr(
                EmotionalState, emotion_name.upper(), EmotionalState.NEUTRAL)
        except Exception as e:
            print("Error mapping emotion:", e)
            emotional_state = EmotionalState.NEUTRAL

        try:
            if emotion_conf > 0.6:
                engagement = EngagementLevel.HIGH
            elif horizontal in [HEAD_POSE_MAPPING.get("Left"), HEAD_POSE_MAPPING.get("Right"), HEAD_POSE_MAPPING.get("Down")]:
                engagement = EngagementLevel.LOW
            else:
                engagement = EngagementLevel.MEDIUM
        except Exception as e:
            print("Error determining engagement level:", e)
            engagement = EngagementLevel.MEDIUM

        try:
            mode = Mode.INTERACTION if gaze != GAZE_MAPPING.get(
                "Looking center", 0) else Mode.NARRATION
        except Exception as e:
            print("Error determining mode:", e)
            mode = Mode.NARRATION

        response_quality = ResponseQuality.AVERAGE
        prompt_necessity = PromptNecessity.NO
        response_length = ResponseLength.MEDIUM
        vocabulary_usage = VocabularyUsage.MEDIUM

        try:
            if mode == Mode.NARRATION:
                new_state = State(mode, engagement, emotional_state)
            else:
                new_state = State(mode, engagement, emotional_state, response_quality,
                                  prompt_necessity, response_length, vocabulary_usage)
        except Exception as e:
            print("Error creating state object:", e)
            new_state = State(
                Mode.NARRATION, EngagementLevel.MEDIUM, EmotionalState.NEUTRAL)

        print("Updated State:", new_state)
        self.current_state = new_state
        return new_state

# ----------------------------------------------------------
# NEW FUNCTION
# ----------------------------------------------------------

    def update_state_from_story(self, mode, child_response):
        """
        Update the state based on the storytelling context.

        Parameters:
          mode (Mode): The current mode (e.g., Mode.NARRATION or Mode.INTERACTION).
          child_response (str): The child's spoken response.

        Returns:
          State: An updated state object reflecting the current interaction.
        """
        if mode == Mode.INTERACTION:
            words = child_response.split()
            if len(words) >= 10:
                engagement = EngagementLevel.HIGH
            elif 1 <= len(words) < 10:
                engagement = EngagementLevel.MEDIUM
            else:
                engagement = EngagementLevel.LOW
        else:
            engagement = EngagementLevel.MEDIUM

        emotional_state = EmotionalState.NEUTRAL

        if mode == Mode.INTERACTION:
            num_words = len(child_response.split())
            if num_words >= 15:
                response_quality = ResponseQuality.STRONG
            elif num_words >= 5:
                response_quality = ResponseQuality.AVERAGE
            else:
                response_quality = ResponseQuality.WEAK

            # Categorize Response Length.
            if num_words < 5:
                response_length = ResponseLength.SHORT
            elif num_words <= 15:
                response_length = ResponseLength.MEDIUM
            else:
                response_length = ResponseLength.LONG

            # Evaluate Vocabulary Usage using a unique/total words ratio.
            words = child_response.split()
            unique_ratio = len(set(words)) / len(words) if words else 0.0
            vocabulary_usage = VocabularyUsage.HIGH if unique_ratio > 0.5 else VocabularyUsage.MEDIUM

            # Detect WH-questions
            wh_words = {"who", "what", "when", "where", "why", "how", "which"}
            # first_word = words[0].lower() if words else ""
            # wh_question_detected = first_word in wh_words
            wh_question_detected = any(
                word.lower() in wh_words for word in words)

            # Determine if a prompt is necessary
            if wh_question_detected or engagement == EngagementLevel.LOW:
                prompt_necessity = PromptNecessity.YES
            else:
                prompt_necessity = PromptNecessity.NO

            # Create the full state for INTERACTION mode.
            new_state = State(mode, engagement, emotional_state,
                              response_quality, prompt_necessity,
                              response_length, vocabulary_usage,
                              wh_question_detected)  # Include WH-question detection
        else:
            new_state = State(mode, engagement, emotional_state)
        self.current_state = new_state
        return new_state

# ----------------------------------------------------------
# ----------------------------------------------------------

    def maybe_update(self):
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            new_state = self.update_state()
            self.last_update_time = current_time
            self.head_horizontal_buffer.clear()
            self.head_vertical_buffer.clear()
            self.gaze_buffer.clear()
            self.emotion_buffer.clear()
            self.emotion_conf_buffer.clear()
            return new_state
        return None

    def get_current_state(self):
        print("Current State:", self.current_state)
        return self.current_state


