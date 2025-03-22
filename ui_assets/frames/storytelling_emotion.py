import threading
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ui_assets.constants import SOFT_PINK, DARK_TEXT, FONT, TITLE_FONT, SOFT_BLUE


class StorytellingEmotionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_PINK)
        self.controller = controller  # Store controller reference
        tk.Label(self, text="Storytelling Session", font=TITLE_FONT,
                 bg=SOFT_PINK, fg=DARK_TEXT).pack(pady=20)

        # Story Image Display
        self.story_canvas = tk.Canvas(
            self, width=650, height=430, bg=SOFT_PINK)
        self.story_canvas.pack(pady=5)

        # Video Feed Placeholder
        self.video_frame = tk.LabelFrame(
            self, text="Video Feed", font=FONT, bg=SOFT_PINK, fg=DARK_TEXT, labelanchor="n")
        self.video_frame.place(relx=0.7, rely=0.05, width=250, height=150)
        self.video_label = tk.Label(self.video_frame, bg=SOFT_PINK)
        self.video_label.pack(expand=True, fill="both")

        # Control Buttons
        controls_frame = tk.Frame(self, bg=SOFT_PINK)
        controls_frame.pack(pady=20)
        tk.Button(controls_frame, text="Pause", font=FONT, bg=SOFT_BLUE,
                  command=self.pause_video).pack(side="left", padx=10)
        tk.Button(controls_frame, text="End", font=FONT, bg=SOFT_BLUE,
                  command=lambda: self.end_storytelling()).pack(side="left", padx=10)

        # Video Capture Variables
        self.cap = None
        self.video_running = False

    def on_show(self):
        """Called when the frame is shown. Start video & storytelling."""
        self.start_video()
        # self.controller.run_storytelling(self)
        threading.Thread(target=self.controller.run_storytelling,
                         args=(self,), daemon=True).start()

    def start_video(self):
        """Start the video capture if it isn't running yet."""
        if not self.video_running:
            self.cap = cv2.VideoCapture(0)  # Open webcam
            self.video_running = True
            self.update_video()

    def update_video(self):
        """Continuously update the video feed with flipping and quality retention."""
        if self.video_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)  # Flip horizontally

                # Retain aspect ratio while resizing (target width = 250)
                height, width, _ = frame.shape
                aspect_ratio = height / width
                new_width = 250
                # Maintain aspect ratio
                new_height = int(new_width * aspect_ratio)

                frame = cv2.resize(frame, (new_width, new_height),
                                   interpolation=cv2.INTER_LINEAR)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                img = Image.fromarray(frame)
                img_tk = ImageTk.PhotoImage(image=img)
                self.video_label.img_tk = img_tk  # Prevent garbage collection
                self.video_label.config(image=img_tk)

            self.after(30, self.update_video)

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
        self.controller.next_frame("Storytelling")
