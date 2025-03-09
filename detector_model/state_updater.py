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
        self.head_horizontal_buffer = deque(maxlen=100)  # adjust maxlen as needed
        self.head_vertical_buffer = deque(maxlen=100)
        self.gaze_buffer = deque(maxlen=100)
        self.emotion_buffer = deque(maxlen=100)
        self.emotion_conf_buffer = deque(maxlen=100)
        
        self.last_update_time = time.time()
        self.update_interval = update_interval  # seconds
        
    def add_reading(self, horizontal, vertical, gaze, emotion, emotion_conf):
        self.head_horizontal_buffer.append(horizontal)
        self.head_vertical_buffer.append(vertical)
        self.gaze_buffer.append(gaze)
        self.emotion_buffer.append(emotion)
        self.emotion_conf_buffer.append(emotion_conf)
    
    def aggregate_head_pose(self):
        # Convert stored labels to numeric values
        horizontal_values = [HEAD_POSE_MAPPING[pose] for pose in self.head_horizontal_buffer if pose in HEAD_POSE_MAPPING]
        vertical_values = [HEAD_POSE_MAPPING[pose] for pose in self.head_vertical_buffer if pose in HEAD_POSE_MAPPING]

        # Find the most common (mode) for stability
        horizontal_mode = Counter(horizontal_values).most_common(1)[0][0] if horizontal_values else HEAD_POSE_MAPPING["Front"]
        vertical_mode = Counter(vertical_values).most_common(1)[0][0] if vertical_values else HEAD_POSE_MAPPING["Front"]

        return horizontal_mode, vertical_mode

    def aggregate_gaze(self):
        if self.gaze_buffer:
            gaze_mode = Counter(self.gaze_buffer).most_common(1)[0][0]
            return GAZE_MAPPING.get(gaze_mode, 0)  # Default to center (0) if unknown
        else:
            return 0  # Default to center (0) if buffer is empty

    def aggregate_emotion(self):
        # If no emotions are recorded, return Neutral with 0.0 confidence
        if not self.emotion_buffer:
            return 4, 0.0  # Neutral (4) and 0.0 confidence

        # Find the most common emotion
        counts = Counter(self.emotion_buffer)
        most_common_emotion, count = counts.most_common(1)[0]

        # Compute average confidence for occurrences of that emotion
        confs = [conf for emo, conf in zip(self.emotion_buffer, self.emotion_conf_buffer) if emo == most_common_emotion]
        avg_conf = statistics.mean(confs) if confs else 0.0

        # Return the mapped numeric value and average confidence
        return EMOTION_MAPPING.get(most_common_emotion, 4), avg_conf 

    def update_state(self):
        """Aggregates sensor data and updates the state based on predefined logic."""
    
        # Aggregate head pose, gaze, and emotion
        horizontal, vertical = self.aggregate_head_pose()
        gaze = self.aggregate_gaze()
        emotion_idx, emotion_conf = self.aggregate_emotion()  # Returns numeric emotion index and confidence
    
        # **Map emotion index to EmotionalState enum**
        emotion_list = list(EMOTION_MAPPING.keys())  # Get emotion names in order
        emotion_name = emotion_list[emotion_idx] if emotion_idx in range(len(emotion_list)) else "Neutral"
        emotional_state = getattr(EmotionalState, emotion_name.upper(), EmotionalState.NEUTRAL)
    
        # **Determine Engagement Level**
        if emotion_conf > 0.6:  # High confidence in emotion
            engagement = EngagementLevel.HIGH
        elif horizontal in [HEAD_POSE_MAPPING["Left"], HEAD_POSE_MAPPING["Right"], HEAD_POSE_MAPPING["Down"]]:
            engagement = EngagementLevel.LOW  # Looking away decreases engagement
        else:
            engagement = EngagementLevel.MEDIUM
    
        # **Determine Mode**
        mode = Mode.INTERACTION if gaze != GAZE_MAPPING["Looking center"] else Mode.NARRATION
    
        # **Set Default Interaction Values**
        response_quality = ResponseQuality.AVERAGE
        prompt_necessity = PromptNecessity.NO
        response_length = ResponseLength.MEDIUM
        vocabulary_usage = VocabularyUsage.MEDIUM
    
        # **Create State Object**
        if mode == Mode.NARRATION:
            new_state = State(mode, engagement, emotional_state)
        else:
            new_state = State(mode, engagement, emotional_state, response_quality,
                              prompt_necessity, response_length, vocabulary_usage)
    
        print("Updated State:", new_state)
        return new_state


    def maybe_update(self):
        # Check if it's time to update the state based on the interval
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