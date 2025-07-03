import cv2
import dlib
import numpy as np
import math
from fer import FER
from gaze_tracking import GazeTracking
import os
# from state_updater import StateUpdater


class FaceAnalyzer:
    """Handles face detection, gaze tracking, and head pose estimation."""

    def __init__(self, predictor_path):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)
        self.gaze = GazeTracking()
        self.model_points = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye left corner
            (225.0, 170.0, -135.0),      # Right eye right corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ])

    def detect_faces(self, gray_frame):
        """Detect faces in a grayscale image."""
        return self.detector(gray_frame)

    def get_landmarks(self, gray_frame, face):
        """Return face landmarks for a given face."""
        return self.predictor(gray_frame, face)

    def get_head_pose(self, landmarks, frame_size):
        """Estimate head pose based on facial landmarks."""
        image_points = np.array([
            (landmarks.part(30).x, landmarks.part(30).y),  # Nose tip
            (landmarks.part(8).x, landmarks.part(8).y),    # Chin
            (landmarks.part(36).x, landmarks.part(36).y),  # Left eye left corner
            (landmarks.part(45).x, landmarks.part(45).y),  # Right eye right corner
            (landmarks.part(48).x, landmarks.part(48).y),  # Left mouth corner
            (landmarks.part(54).x, landmarks.part(54).y)   # Right mouth corner
        ], dtype="double")

        focal_length = frame_size[1]
        center = (frame_size[1] // 2, frame_size[0] // 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")

        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        success, rotation_vector, _ = cv2.solvePnP(
            self.model_points, image_points, camera_matrix, dist_coeffs)

        return rotation_vector if success else None

    def get_gaze_direction(self, frame):
        """Detects gaze direction using GazeTracking library."""
        self.gaze.refresh(frame)

        if self.gaze.is_right():
            return "Looking Right"
        elif self.gaze.is_left():
            return "Looking Left"
        elif self.gaze.is_center():
            return "Looking Center"
        return "Unknown"

    @staticmethod
    def rotation_vector_to_euler_angles(rotation_vector):
        """Convert rotation vector to yaw, pitch, roll angles."""
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        pitch = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
        yaw = math.atan2(-rotation_matrix[2, 0], np.sqrt(
            rotation_matrix[2, 1]**2 + rotation_matrix[2, 2]**2))
        roll = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        return math.degrees(yaw), math.degrees(pitch), math.degrees(roll)

    @staticmethod
    def get_horizontal_movement_label(yaw):
        """Determine head movement direction based on yaw."""
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

    @staticmethod
    def get_vertical_movement_label(pitch):
        """Determine head movement direction based on pitch."""
        if pitch < -10:
            return "Down"
        elif pitch > 0 and pitch <= 160:
            return "Up"
        return "Front"


class EmotionAnalyzer:
    """Handles emotion detection from facial expressions."""

    def __init__(self):
        self.detector = FER()
        self.last_emotion = "Neutral"
        self.last_score = 0.0

    def detect_emotion(self, frame):
        """Run emotion detection and return the most likely emotion."""
        result = self.detector.detect_emotions(frame)
        if result:
            emotion, score = self.detector.top_emotion(frame)
            if emotion:
                self.last_emotion = emotion
                self.last_score = round(score, 2)
        return self.last_emotion, self.last_score


class VideoProcessor:
    """Handles video processing (head pose, gaze tracking, and emotions)."""

    def __init__(self, predictor_path):
        self.face_analyzer = FaceAnalyzer(predictor_path)
        self.emotion_analyzer = EmotionAnalyzer()
        self.cap = cv2.VideoCapture(1)
        self.frame_count = 0
        self.emotion_update_interval = 15  # Run emotion detection every 15 frames

        self.horizontal_label = None
        self.vertical_label = None
        self.gaze_direction = None
        self.last_emotion = None
        self.last_score = None

    def process_frame(self):
        """Processes a single frame and updates the detected values."""
        ret, frame = self.cap.read()
        if not ret:
            return None

        self.frame_count += 1
        frame_resized = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        faces = self.face_analyzer.detect_faces(gray)

        for face in faces:
            landmarks = self.face_analyzer.get_landmarks(gray, face)

            # Get head pose
            rotation_vector = self.face_analyzer.get_head_pose(
                landmarks, frame_resized.shape)
            if rotation_vector is not None:
                yaw, pitch, _ = self.face_analyzer.rotation_vector_to_euler_angles(
                    rotation_vector)
                self.horizontal_label = self.face_analyzer.get_horizontal_movement_label(
                    yaw)
                self.vertical_label = self.face_analyzer.get_vertical_movement_label(
                    pitch)

            # Get gaze direction
            self.gaze_direction = self.face_analyzer.get_gaze_direction(
                frame_resized)

            # Get emotion every self.emotion_update_interval frames
            if self.frame_count % self.emotion_update_interval == 0:
                emotion, score = self.emotion_analyzer.detect_emotion(
                    frame_resized)
                self.last_emotion = emotion
                self.last_score = score

        return frame_resized

    def get_latest_state(self):
        """Returns the latest detected head pose, gaze, and emotion."""
        return {
            "horizontal": self.horizontal_label,
            "vertical": self.vertical_label,
            "gaze": self.gaze_direction,
            "emotion": self.last_emotion,
            "score": self.last_score
        }

    def release(self):
        """Releases the video capture resources."""
        self.cap.release()
        cv2.destroyAllWindows()
