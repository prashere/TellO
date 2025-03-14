import tkinter as tk
from ui_assets.constants import SOFT_PINK, WHITE, DARK_TEXT, FONT, TITLE_FONT, SOFT_BLUE

class StorytellingEmotionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_PINK)

        tk.Label(self, text="Storytelling Session", font=TITLE_FONT, bg=SOFT_PINK, fg=DARK_TEXT).pack(pady=20)

        # Placeholder for Story Image
        story_canvas = tk.Canvas(self, width=650, height=430, bg=WHITE)
        story_canvas.pack(pady=5)

        # Video Feed Placeholder
        video_frame = tk.LabelFrame(self, text="Video Feed", font=FONT, bg=WHITE, fg=DARK_TEXT, labelanchor="n")
        video_frame.place(relx=0.7, rely=0.05, width=250, height=150)
        tk.Label(video_frame, text="Video Feed Here", font=("Arial", 10), bg=WHITE, fg=DARK_TEXT).pack(expand=True, fill="both")

        # Control Buttons
        controls_frame = tk.Frame(self, bg=SOFT_PINK)
        controls_frame.pack(pady=20)

        tk.Button(controls_frame, text="Pause", font=FONT, bg=SOFT_BLUE, command=lambda: print("Paused")).pack(side="left", padx=10)
        tk.Button(controls_frame, text="End", font=FONT, bg=SOFT_BLUE, command=lambda: controller.next_frame("Storytelling")).pack(side="left", padx=10)
