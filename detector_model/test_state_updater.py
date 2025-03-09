from .state_updater import *

s = StateUpdater()

s.add_reading("Left", "Up", "Looking left", "Happy", 0.8)
s.add_reading("Right", "Up", "Blinking", "Happy", 0.8)
s.add_reading("Left", "Down", "Looking left", "Happy", 0.8)
s.add_reading("Left", "Down", "Looking center", "Happy", 0.8)
s.add_reading("Front", "Front", "Looking center", "Happy", 0.8)
s.add_reading("Front", "Front", "Looking center", "Happy", 0.8)
s.add_reading("Left", "Up", "", "Happy", 0.8)
s.add_reading("Left", "Up", "Blinking", "Happy", 0.8)

# Head Pose Testing
print(s.aggregate_head_pose())

# Gaze Testing
print(s.aggregate_gaze())

# Emotion and confidence
e, score = s.aggregate_emotion()
print("Emotion ",e,"Confidence ",score)
