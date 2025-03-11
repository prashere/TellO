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
            horizontal_values = [HEAD_POSE_MAPPING[pose] for pose in self.head_horizontal_buffer if pose in HEAD_POSE_MAPPING]
            vertical_values = [HEAD_POSE_MAPPING[pose] for pose in self.head_vertical_buffer if pose in HEAD_POSE_MAPPING]
            horizontal_mode = Counter(horizontal_values).most_common(1)[0][0] if horizontal_values else HEAD_POSE_MAPPING["Front"]
            vertical_mode = Counter(vertical_values).most_common(1)[0][0] if vertical_values else HEAD_POSE_MAPPING["Front"]
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
            confs = [conf for emo, conf in zip(self.emotion_buffer, self.emotion_conf_buffer) if emo == most_common_emotion and conf is not None]
            avg_conf = statistics.mean(confs) if confs else 0.0
            return EMOTION_MAPPING.get(most_common_emotion, 4), avg_conf 
        except Exception as e:
            print("Error in aggregate_emotion:", e)
            return 4, 0.0

    def update_state(self):
        try:
            horizontal, vertical = self.aggregate_head_pose()
            gaze = self.aggregate_gaze()
            emotion_idx, emotion_conf = self.aggregate_emotion()  # Returns numeric emotion index and confidence
        except Exception as e:
            print("Error during state aggregation:", e)
            horizontal, vertical, gaze, emotion_idx, emotion_conf = HEAD_POSE_MAPPING["Front"], HEAD_POSE_MAPPING["Front"], 0, 4, 0.0

        try:
            # Map emotion index to EmotionalState enum
            emotion_list = list(EMOTION_MAPPING.keys())
            emotion_name = emotion_list[emotion_idx] if emotion_idx in range(len(emotion_list)) else "Neutral"
            emotional_state = getattr(EmotionalState, emotion_name.upper(), EmotionalState.NEUTRAL)
        except Exception as e:
            print("Error mapping emotion:", e)
            emotional_state = EmotionalState.NEUTRAL

        try:
            # Determine Engagement Level
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
            # Determine Mode based on gaze
            mode = Mode.INTERACTION if gaze != GAZE_MAPPING.get("Looking center", 0) else Mode.NARRATION
        except Exception as e:
            print("Error determining mode:", e)
            mode = Mode.NARRATION

        # Set default interaction values if needed
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
            new_state = State(Mode.NARRATION, EngagementLevel.MEDIUM, EmotionalState.NEUTRAL)
        
        print("Updated State:", new_state)
        return new_state

    def maybe_update(self):
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            new_state = self.update_state()
            self.last_update_time = current_time
            # Optionally, clear the buffers after updating the state
            self.head_horizontal_buffer.clear()
            self.head_vertical_buffer.clear()
            self.gaze_buffer.clear()
            self.emotion_buffer.clear()
            self.emotion_conf_buffer.clear()
            return new_state
        return None



if __name__ == "__main__":
    updater = StateUpdater(update_interval=60)  # update state every 60 seconds
    while True:
        # In your main loop, after processing sensor data from your detector:
        # For example, assume you have the following variables updated by your sensor code:
        # detected_horizontal: the horizontal head pose label ("Left", "Front", etc.)
        # detected_vertical: the vertical head pose label ("Up", "Down", etc.)
        # detected_gaze: gaze status ("Looking left", "Looking center", etc.)
        # detected_emotion: emotion string (e.g., "Happy", "Sad", etc.)
        # detected_emotion_conf: confidence score (e.g., 0.85)
        # These values come from your current code (the one you pasted above).

        # For demonstration, let's assume:
        detected_horizontal = "Left"
        detected_vertical = "Up"
        detected_gaze = "Looking left"
        detected_emotion = "Happy"
        detected_emotion_conf = 0.90
        print("here")
        # Add the current sensor readings to the buffers
        updater.add_reading(detected_horizontal, detected_vertical,
                            detected_gaze, detected_emotion, detected_emotion_conf)

        # Call maybe_update periodically (e.g., every frame)
        state = updater.maybe_update()
        if state is not None:
            # Do something with the new state, like feed it to your RL agent or log it.
            pass

        # Sleep or wait for the next frame (simulate frame rate)
        time.sleep(1)