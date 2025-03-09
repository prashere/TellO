import time
import os
import cv2
from detector_model.head_gaze_emotion_detector import VideoProcessor
from detector_model.state_updater import StateUpdater

# Initialize paths and objects
predictor_path = "./detector_model/assets/shape_predictor_68_face_landmarks.dat"

if not os.path.exists(predictor_path):
    raise FileNotFoundError(f"Model file not found: {predictor_path}")

video_processor = VideoProcessor(predictor_path)
state_updater = StateUpdater(update_interval=10)

# Keep track of the last update time
last_update_time = time.time()

while True:
    frame = video_processor.process_frame()
    if frame is None:
        break

    # Get the latest detected state
    latest_state = video_processor.get_latest_state()

    # **Only update the state every second**
    current_time = time.time()
    if current_time - last_update_time >= 1:
        state_updater.add_reading(
            latest_state["horizontal"],
            latest_state["vertical"],
            latest_state["gaze"],
            latest_state["emotion"],
            latest_state["score"]
        )
        last_update_time = current_time  # Reset timer

    # **Check if it's time to update the full state (every 60s)**
    updated_state = state_updater.maybe_update()
    if updated_state:
        print("State Updated:", updated_state)  # Send this to RL or logging system

    # **Display Information**
    cv2.putText(frame, f"Horizontal: {latest_state['horizontal']}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"Vertical: {latest_state['vertical']}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    cv2.putText(frame, f"Gaze: {latest_state['gaze']}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    if latest_state["emotion"]:
        cv2.putText(frame, f"Emotion: {latest_state['emotion']} ({latest_state['score']})",
                    (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    cv2.imshow("Head Pose, Gaze, and Emotion Detection", frame)

    # **Press 'q' to quit**
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
video_processor.release()
