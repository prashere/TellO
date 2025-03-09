import cv2
import dlib
import numpy as np
import math
from fer import FER
from gaze_tracking import GazeTracking
import os
print(os.path.exists("./detector_model/assets/shape_predictor_68_face_landmarks.dat"))



# Loading Dlib's face detector and 68-point landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    "./detector_model/assets/shape_predictor_68_face_landmarks.dat")  # Ensure this file is correct

# Initialize emotion detector
emotion_detector = FER()

# Initialize gaze tracker
gaze = GazeTracking()

# 3D model points for head pose estimation
model_points = np.array([
    (0.0, 0.0, 0.0),             # Nose tip
    (0.0, -330.0, -65.0),        # Chin
    (-225.0, 170.0, -135.0),     # Left eye left corner
    (225.0, 170.0, -135.0),      # Right eye right corner
    (-150.0, -150.0, -125.0),    # Left mouth corner
    (150.0, -150.0, -125.0)      # Right mouth corner
])

# Start video capture
cap = cv2.VideoCapture(0)


def rotation_vector_to_euler_angles(rotation_vector):
    """Converts the rotation vector to Euler angles."""
    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    pitch = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
    yaw = math.atan2(-rotation_matrix[2, 0], np.sqrt(
        rotation_matrix[2, 1]**2 + rotation_matrix[2, 2]**2))
    roll = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
    return math.degrees(yaw), math.degrees(pitch), math.degrees(roll)


def get_horizontal_movement_label(yaw):
    """Estimate horizontal head position based on yaw."""
    if yaw < -15:
        return "Left"
    elif -15 <= yaw < -5:
        return "Slight Left"
    elif -5 <= yaw <= 5:
        return "Front"
    elif 5 < yaw <= 15:
        return "Slight Right"
    elif yaw > 15:
        return "Right"
    return "Front"


def get_vertical_movement_label(pitch):
    """Estimate vertical head position based on pitch."""
    if pitch < -10:
        return "Down"
    elif pitch > 0 and pitch <= 160:
        return "Up"
    return "Front"


# Variables for smoothing
last_horizontal_label = "Front"
last_vertical_label = "Front"
last_emotion = "Neutral"
gaze_text = "Front"
last_emotion_score = 0.00
frame_count = 0
emotion_update_interval = 15  # Run emotion detection every 15 frames

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    frame_resized = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)


    for face in faces:
        gaze.refresh(frame_resized)

        landmarks = predictor(gray, face)

        # 2D image points for face landmarks
        image_points = np.array([
            (landmarks.part(30).x, landmarks.part(30).y),  # Nose tip
            (landmarks.part(8).x, landmarks.part(8).y),    # Chin
            (landmarks.part(36).x, landmarks.part(36).y),  # Left eye left corner
            (landmarks.part(45).x, landmarks.part(45).y),  # Right eye right corner
            (landmarks.part(48).x, landmarks.part(48).y),  # Left mouth corner
            (landmarks.part(54).x, landmarks.part(54).y)   # Right mouth corner
        ], dtype="double")

        # Camera matrix
        size = frame_resized.shape
        focal_length = size[1]
        center = (size[1] // 2, size[0] // 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")

        # Solve PnP
        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points, image_points, camera_matrix, dist_coeffs)

        # Convert rotation vector to Euler angles
        yaw, pitch, roll = rotation_vector_to_euler_angles(rotation_vector)

        # Get movement labels
        horizontal_movement_label = get_horizontal_movement_label(yaw)
        vertical_movement_label = get_vertical_movement_label(pitch)

        # Smooth movement updates
        if horizontal_movement_label != last_horizontal_label:
            last_horizontal_label = horizontal_movement_label
        if vertical_movement_label != last_vertical_label:
            last_vertical_label = vertical_movement_label

        if gaze.is_blinking():
            gaze_text = "Blinking"
        elif gaze.is_right():
            gaze_text = "Looking right"
        elif gaze.is_left():
            gaze_text = "Looking left"
        elif gaze.is_center():
            gaze_text = "Looking center"

        # Display movement labels
        cv2.putText(frame_resized, f"Horizontal: {last_horizontal_label}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame_resized, f"Vertical: {last_vertical_label}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
         # Draw cross at the center of the eyes (gaze tracking)
        left_eye_center = (landmarks.part(36).x + landmarks.part(39).x) // 2, (landmarks.part(36).y + landmarks.part(39).y) // 2
        right_eye_center = (landmarks.part(42).x + landmarks.part(45).x) // 2, (landmarks.part(42).y + landmarks.part(45).y) // 2

        cv2.drawMarker(frame_resized, left_eye_center, (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
        cv2.drawMarker(frame_resized, right_eye_center, (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
        # print(f"Gaze: {gaze_text}")
        cv2.putText(frame_resized, f"Gaze: {gaze_text}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Run emotion detection every `emotion_update_interval` frames
    if frame_count % emotion_update_interval == 0:
        result = emotion_detector.detect_emotions(frame_resized)
        if result:
            emotion, score = emotion_detector.top_emotion(frame_resized)
            last_emotion = emotion if emotion else last_emotion
            last_emotion_score = round(score, 2)

    # Display emotion label (persists until updated)
    cv2.putText(frame_resized, f"Emotion: {last_emotion} ({last_emotion_score})", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    cv2.imshow("Head Pose and Emotion Detection", frame_resized)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
