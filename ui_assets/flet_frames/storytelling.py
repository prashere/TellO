import asyncio
import threading
import time
import cv2
import datetime
import base64
from io import BytesIO
from PIL import Image
import requests
import flet as ft
from detector_model.head_gaze_emotion_detector import FaceAnalyzer, EmotionAnalyzer


class StorytellingEmotionFrame(ft.Container):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.page = app.page

        # Video & detection state
        self.video_running = False
        self.cap = None

        self.last_horizontal_movement = "Center"
        self.last_vertical_movement = "Center"
        self.last_gaze_direction = "Forward"
        self.last_emotion = "Neutral"
        self.last_emotion_confidence = 0.0

        # Shared variable for the latest frame.
        self._latest_img_str = None

        predictor_path = "./detector_model/assets/shape_predictor_68_face_landmarks.dat"
        self.face_analyzer = FaceAnalyzer(predictor_path)
        self.emotion_analyzer = EmotionAnalyzer()

        # UI Widgets
        self.video_image = ft.Image(
            width=450, height=250, fit=ft.ImageFit.CONTAIN)
        self.status_text = ft.Text(
            "Detecting...", size=14, color=ft.colors.BLACK)

        self.state_text = ft.Text("Hear Me 😁", weight=ft.FontWeight.BOLD,
                                  size=16,
                                  color=ft.colors.BLACK,
                                  text_align=ft.TextAlign.CENTER)
        self.speak_status_text = self.state_text

        self.story_image = ft.Image(
            width=650, height=430, fit=ft.ImageFit.CONTAIN)

        self.content = self.build()

    def get_head_pose(self):
        """Returns the last detected head movement."""
        return self.last_horizontal_movement, self.last_vertical_movement

    def get_gaze(self):
        """Returns the last detected gaze direction."""
        return self.last_gaze_direction

    def get_emotion(self):
        """Returns the last detected emotion and its confidence."""
        return self.last_emotion, self.last_emotion_confidence

    def monitor_app_state(self):
        prev_state = None
        while self.video_running:
            current_state = self.app.state
            if current_state != prev_state:
                prev_state = current_state
                self.update_speak_status(current_state)
                try:
                    self.page.update()
                except RuntimeError as e:
                    print("RuntimeError in monitor_app_state:", e)
                    break
            time.sleep(0.5)  

    def build(self):
        # Color and style constants
        BACKGROUND_COLOR = "#FFF7ED"  
        WHITE_COLOR = "#FFFFFF"         
        TEXT_COLOR = "#333333"

        self.speak_status_container = ft.Container(
            content=self.state_text,
            bgcolor=ft.colors.LIME_400,
            padding=15,
            border_radius=ft.border_radius.all(12),
            alignment=ft.alignment.center,
            width=180,
            height=50,
        )

        # Right side: Story Image Section (similar to teacher verification)
        story_image_section = ft.Container(
            content=self.story_image,
            bgcolor=WHITE_COLOR,
            border_radius=ft.border_radius.only(top_right=30, bottom_right=30),
            expand=True,
            height=650,
            margin=ft.margin.only(right=20),
        )

        # Left side: White container with video and info.
        # Video Card: a larger video frame wrapped in a card.
        video_card = ft.Container(
            content=self.video_image,
            # width=380,
            # height=250,
            border_radius=ft.border_radius.all(12),
            padding=5,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.WHITE,  # Optional: background inside the border
        )

        info_row = ft.Row(
            controls=[
                self.status_text,
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        speak_listen_row = ft.Row(
            controls=[
                self.speak_status_container
            ],
            spacing=30,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        button_row = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Pause",
                    on_click=lambda e: self.pause_video(),
                    bgcolor=ft.colors.AMBER_400,
                    color=TEXT_COLOR,
                    width=130,
                    height=45,
                ),
                ft.ElevatedButton(
                    "End",
                    on_click=lambda e: self.end_storytelling(),
                    bgcolor=ft.colors.AMBER_400,
                    color=ft.colors.BLACK,
                    width=130,
                    height=45,
                ),
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Title section at the top with a horizontal divider.
        title_section = ft.Column(
            controls=[
                ft.Text("Good Luck 🎈", size=24, weight="bold",
                        color=ft.colors.BLACK, text_align="center"),
                ft.Divider(color=ft.colors.GREY_300, thickness=1),
            ],
            horizontal_alignment="center",
        )
        left_container = ft.Container(
            content=ft.Column(
                controls=[
                    title_section,
                    video_card,
                    info_row,
                    speak_listen_row,
                    button_row,
                ],
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.colors.WHITE,
            padding=20,
            border_radius=ft.border_radius.only(top_left=30, bottom_left=30),
            width=550,
            height=650,
            margin=ft.margin.only(left=20),
        )

        main_content_row = ft.Row(
            controls=[
                left_container,
                story_image_section,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            expand=True,

        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    main_content_row,
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=BACKGROUND_COLOR,
            expand=True,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=10, spread_radius=1,
                                color=ft.colors.GREY_400, offset=ft.Offset(2, 2)),
        )

    def update_speak_status(self, new_state):
        self.state = new_state
        if self.state == "idle":
            self.state_text.value = "Hear Me 😁"
            self.page.update()

        elif self.state == "listening":
            self.state_text.value = "Speak Now 🎤"
            self.page.update()
            time.sleep(2)
            self.state_text.value = "Listening.......👂"
            self.page.update()


    def on_mount(self):
        print("Storytelling Frame mounted: starting video and analysis.")
        # self.start_video()
        # threading.Thread(target=self.analyze_video_frame, daemon=True).start()
        # threading.Thread(target=self.app.run_storytelling(self), daemon=True).start()
        # threading.Thread(target=self.app.run_storytelling, args=(self,), daemon=True).start()
        self.app.session_start_time = datetime.datetime.now().isoformat()
        self.app.story_id = 4

    def start_video(self):
        if not self.video_running:
            self.cap = cv2.VideoCapture(1)
            if not self.cap.isOpened():
                print("Error: Unable to open webcam.")
                return
            self.video_running = True
            print("Video capture started.")
            threading.Thread(target=self.analyze_video_frame,
                             daemon=True).start()
            threading.Thread(target=self.update_video, daemon=True).start()
            threading.Thread(target=self.monitor_app_state,daemon=True).start()
            
    def update_video(self):
        while self.video_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                height, width, _ = frame.shape
                new_width = 250
                aspect_ratio = height / width
                new_height = int(new_width * aspect_ratio)
                frame = cv2.resize(frame, (new_width, new_height),
                                   interpolation=cv2.INTER_LINEAR)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                im = Image.fromarray(frame)
                buffer = BytesIO()
                im.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
                self._latest_img_str = img_str
                try:
                    self.video_image.src_base64 = self._latest_img_str
                    self.page.update()
                except RuntimeError as e:
                    print("RuntimeError during page.update():", e)
                    break  # Break out of the loop if event loop is closed.
            else:
                print("Warning: Frame not captured.")
            time.sleep(0.03)

    def analyze_video_frame(self):
        # Analyze a frame every 5 seconds.
        while self.video_running:
            if self.cap:
                ret, frame = self.cap.read()
            else:
                ret = False
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
                        detected_state = {
                            "horizontal": self.last_horizontal_movement,
                            "vertical": self.last_vertical_movement,
                            "gaze": self.last_gaze_direction,
                            "emotion": self.last_emotion,
                            "emotion_confidence": self.last_emotion_confidence,
                        }
                        self.app.update_storytelling_state(detected_state)
                        analysis_text = (
                            f"Emotion: {self.last_emotion} ({self.last_emotion_confidence * 100:.1f}%) | "
                            f"Head: H {self.last_horizontal_movement}, V {self.last_vertical_movement} | "
                            f"Gaze: {self.last_gaze_direction}"
                        )
                        
                        self.status_text.value = analysis_text
                        try:
                            self.page.update()
                        except RuntimeError as e:
                            print(
                                "RuntimeError during page.update() in analyze_video_frame:", e)
                            break
                else:
                    self.status_text.value = "No face detected"
                    try:
                        self.page.update()
                    except RuntimeError as e:
                        print("RuntimeError during page.update() (no face):", e)
                        break
            else:
                print("Warning: Unable to capture frame for analysis.")
            
            time.sleep(5)

    def pause_video(self):
        self.video_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        print("Video capture paused.")

    def load_story_image(self, image_path):
        try:
            im = Image.open(image_path)
            im.thumbnail((650, 430))
            buffer = BytesIO()
            im.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            self.story_image.src_base64 = img_str
            self.page.update()
        except Exception as e:
            print("Error loading story image:", e)

    def end_storytelling(self):
        self.pause_video()
        end_time = datetime.datetime.now().isoformat()
        payload = {
            "student_id": self.app.selected_student_id,
            "story_id": self.app.story_id,
            "start_time": self.app.session_start_time,
            "end_time": end_time,
        }
        print("Payload ::", payload)
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/create-story-session/", json=payload)
            if response.status_code == 201:
                dlg = ft.AlertDialog(
                    title=ft.Text("Session Saved"),
                    content=ft.Text("Story session has been recorded."),
                    actions=[ft.TextButton(
                        "OK", on_click=lambda e: dlg.close())],
                )
                self.page.dialog = dlg
                dlg.open = True
                self.page.update()
                self.app.session_id = response.json().get("session_id")
            else:
                dlg = ft.AlertDialog(
                    title=ft.Text("Error"),
                    content=ft.Text("Failed to record the story session."),
                    actions=[ft.TextButton(
                        "OK", on_click=lambda e: dlg.close())],
                )
                self.page.dialog = dlg
                dlg.open = True
                self.page.update()
        except requests.exceptions.RequestException as e:
            dlg = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"Server Error: {e}"),
                actions=[ft.TextButton("OK", on_click=lambda e: dlg.close())],
            )
            self.page.dialog = dlg
            dlg.open = True
            self.page.update()
        self.app.next_frame()


def build_storytelling_frame(app):
    return StorytellingEmotionFrame(app)
