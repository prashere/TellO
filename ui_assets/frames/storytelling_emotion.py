import threading
import time
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import requests
from ui_assets.constants import SOFT_PINK, DARK_TEXT, FONT, TITLE_FONT, SOFT_BLUE
# Import detectors
from detector_model.head_gaze_emotion_detector import FaceAnalyzer, EmotionAnalyzer
import datetime


class StorytellingEmotionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_PINK)
        self.controller = controller
        tk.Label(self, text="Storytelling Session", font=TITLE_FONT,
                 bg=SOFT_PINK, fg=DARK_TEXT).pack(pady=20)

        # Story Image Display
        self.story_canvas = tk.Canvas(
            self, width=650, height=430, bg=SOFT_PINK)
        self.story_canvas.pack(pady=5)

        # Video Feed Display
        self.video_frame = tk.LabelFrame(
            self, text="Video Feed", font=FONT, bg=SOFT_PINK, fg=DARK_TEXT, labelanchor="n")
        self.video_frame.place(relx=0.7, rely=0.05, width=250, height=150)
        self.video_label = tk.Label(self.video_frame, bg=SOFT_PINK)
        self.video_label.pack(expand=True, fill="both")

        # Status Label for Analysis
        self.status_label = tk.Label(
            self, text="Detecting...", font=FONT, bg=SOFT_PINK, fg=DARK_TEXT)
        self.status_label.pack(pady=10)

        # Control Buttons
        controls_frame = tk.Frame(self, bg=SOFT_PINK)
        controls_frame.pack(pady=20)
        tk.Button(controls_frame, text="Pause", font=FONT, bg=SOFT_BLUE,
                  command=self.pause_video).pack(side="left", padx=10)
        tk.Button(controls_frame, text="End", font=FONT, bg=SOFT_BLUE,
                  command=lambda: self.end_storytelling()).pack(side="left", padx=10)

        # Video Processing Variables
        self.cap = None
        self.video_running = False

        # Initialize Face & Emotion Analyzer
        predictor_path = "./detector_model/assets/shape_predictor_68_face_landmarks.dat"
        self.face_analyzer = FaceAnalyzer(predictor_path)
        self.emotion_analyzer = EmotionAnalyzer()

        # Variables to store last detected values
        self.last_horizontal_movement = "Center"
        self.last_vertical_movement = "Center"
        self.last_gaze_direction = "Forward"
        self.last_emotion = "Neutral"
        self.last_emotion_confidence = 0.0

    def on_show(self):
        """Called when the frame is shown. Start video & storytelling."""
        self.start_video()
        threading.Thread(target=self.controller.run_storytelling,
                         args=(self,), daemon=True).start()
        self.controller.session_start_time = datetime.datetime.now().isoformat()
        self.controller.story_id = 4

    def start_video(self):
        """Start the video capture and analysis thread."""
        if not self.video_running:
            self.cap = cv2.VideoCapture(0)  # Open webcam
            self.video_running = True
            self.update_video()
            threading.Thread(target=self.analyze_video_frame,
                             daemon=True).start()  # Start Analysis Thread

    def update_video(self):
        """Continuously update the video feed."""
        if self.video_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)  # Flip horizontally

                # Maintain aspect ratio while resizing
                height, width, _ = frame.shape
                aspect_ratio = height / width
                new_width = 250
                new_height = int(new_width * aspect_ratio)
                frame = cv2.resize(frame, (new_width, new_height),
                                   interpolation=cv2.INTER_LINEAR)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(image=img)
                self.video_label.img_tk = img_tk  # Prevent garbage collection
                self.video_label.config(image=img_tk)

            self.after(30, self.update_video)  # 30 milliseconds

    def analyze_video_frame(self):
        """Analyze head pose, gaze, and emotions every 5 seconds and update the storytelling state."""
        while self.video_running:
            ret, frame = self.cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_analyzer.detect_faces(gray)

                if faces:
                    landmarks = self.face_analyzer.get_landmarks(
                        gray, faces[0])
                    rotation_vector = self.face_analyzer.get_head_pose(
                        landmarks, frame.shape[:2])

                    if rotation_vector is not None:
                        yaw, pitch, roll = self.face_analyzer.rotation_vector_to_euler_angles(
                            rotation_vector)
                        self.last_horizontal_movement = self.face_analyzer.get_horizontal_movement_label(
                            yaw)
                        self.last_vertical_movement = self.face_analyzer.get_vertical_movement_label(
                            pitch)
                        self.last_gaze_direction = self.face_analyzer.get_gaze_direction(
                            frame)
                        self.last_emotion, self.last_emotion_confidence = self.emotion_analyzer.detect_emotion(
                            frame)

                        # Store the detected values
                        detected_state = {
                            "horizontal": self.last_horizontal_movement,
                            "vertical": self.last_vertical_movement,
                            "gaze": self.last_gaze_direction,
                            "emotion": self.last_emotion,
                            "emotion_confidence": self.last_emotion_confidence
                        }

                        self.controller.update_storytelling_state(
                            detected_state)

                        # Update Status Label
                        analysis_text = f"Emotion: {self.last_emotion} ({self.last_emotion_confidence*100:.1f}%) | Head: H {self.last_horizontal_movement}, V {self.last_vertical_movement} | Gaze: {self.last_gaze_direction}"
                        self.status_label.config(text=analysis_text)

                else:
                    self.status_label.config(text="No face detected")

            time.sleep(5)  # Wait for 5 seconds before the next analysis

    def get_head_pose(self):
        """Returns the last detected head movement."""
        return self.last_horizontal_movement, self.last_vertical_movement

    def get_gaze(self):
        """Returns the last detected gaze direction."""
        return self.last_gaze_direction

    def get_emotion(self):
        """Returns the last detected emotion and its confidence."""
        return self.last_emotion, self.last_emotion_confidence

    def pause_video(self):
        """Stop the video feed."""
        self.video_running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def load_story_image(self, image_path):
        """Load and display a story image on the canvas."""
        try:
            img = Image.open(image_path)
            img.thumbnail((650, 430))
            self.story_img = ImageTk.PhotoImage(img)
            self.story_canvas.delete("all")
            self.story_canvas.create_image(325, 215, image=self.story_img)
        except Exception as e:
            print("Error loading story image:", e)

    def end_storytelling(self):
        """Stop video feed and move to the next frame."""
        self.pause_video()
        end_time = datetime.datetime.now().isoformat()
        payload = {
            "student_id": self.controller.selected_student_id,
            "story_id": self.controller.story_id,
            "start_time": self.controller.session_start_time,
            "end_time": end_time
        }
        print('Payload ::', payload)
        url = "http://127.0.0.1:8000/api/create-story-session/"
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 201:
                messagebox.showinfo(
                    "Session Saved", "Story session has been recorded.")
                self.controller.session_id = response.json().get("session_id")
            else:
                messagebox.showerror(
                    "Error", "Failed to record the story session.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Server Error: {e}")
        self.controller.next_frame("Storytelling")
