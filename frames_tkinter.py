import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Colors and Fonts
SOFT_BLUE = "#add8e6"
SOFT_YELLOW = "#ffefa0"
SOFT_GREEN = "#90ee90"
SOFT_PINK = "#ffb6c1"
DARK_TEXT = "#323232"
WHITE = "#ffffff"

FONT = ("Comic Sans MS", 14)
TITLE_FONT = ("Comic Sans MS", 20, "bold")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Child-Friendly Application")
        self.geometry("1000x600")
        self.resizable(False, False)

        # Shared variables for images
        self.logo_img = None
        self.user_icon = None
        self.password_icon = None

        self.frames = {}
        self.current_frame = None

        self.load_images()
        self.create_frames()
        self.show_frame("TeacherVerification")

    def load_images(self):
        """Load and resize images"""
        self.logo_img = ImageTk.PhotoImage(
            Image.open("Images/py_img/teacher.png").resize((300, 220)))
        self.user_icon = ImageTk.PhotoImage(
            Image.open("Images/py_img/user.png").resize((30, 30)))
        self.password_icon = ImageTk.PhotoImage(
            Image.open("Images/py_img/password.png").resize((30, 30)))

    def create_frames(self):
        """Create all the frames for the UI"""
        container = tk.Frame(self, bg=WHITE)
        container.pack(fill="both", expand=True)

        # Add each frame to the app
        self.frames["TeacherVerification"] = TeacherVerificationFrame(
            container, self)
        self.frames["StudentSelection"] = StudentSelectionFrame(
            container, self)
        self.frames["Storytelling"] = StorytellingEmotionFrame(container, self)
        self.frames["EndSession"] = EndSessionFrame(container, self)

    def show_frame(self, frame_name):
        """Switch between frames"""
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(fill="both", expand=True)

    def next_frame(self, current_frame):
        """Switch to the next frame based on the current one"""
        next_frames = {
            "TeacherVerification": "StudentSelection",
            "StudentSelection": "Storytelling",
            "Storytelling": "EndSession",
            "EndSession": "TeacherVerification",
        }
        self.show_frame(next_frames[current_frame])


class TeacherVerificationFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_BLUE)

        # Configure grid to center content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create a container for all content
        content_frame = tk.Frame(self, bg=SOFT_BLUE)
        content_frame.grid(row=0, column=0, sticky="nsew")

        # Logo
        logo_label = tk.Label(
            content_frame, image=controller.logo_img, bg=SOFT_BLUE)
        logo_label.pack(pady=20)

        # Title
        title = tk.Label(content_frame, text="Teacher Verification",
                         font=TITLE_FONT, bg=SOFT_BLUE, fg=DARK_TEXT)
        title.pack()

        # Username Field
        username_frame = tk.Frame(content_frame, bg=SOFT_BLUE)
        username_frame.pack(pady=10)
        tk.Label(username_frame, text="Username:", font=FONT,
                 bg=SOFT_BLUE, fg=DARK_TEXT).pack(side="left")
        tk.Label(username_frame, image=controller.user_icon,
                 bg=SOFT_BLUE).pack(side="left", padx=5)
        tk.Entry(username_frame, font=FONT).pack(side="left")

        # Password Field
        password_frame = tk.Frame(content_frame, bg=SOFT_BLUE)
        password_frame.pack(pady=10)
        tk.Label(password_frame, text="Password:", font=FONT,
                 bg=SOFT_BLUE, fg=DARK_TEXT).pack(side="left")
        tk.Label(password_frame, image=controller.password_icon,
                 bg=SOFT_BLUE).pack(side="left", padx=5)
        tk.Entry(password_frame, font=FONT, show="*").pack(side="left")

        # Login Button
        login_btn = tk.Button(
            content_frame, text="Login", font=FONT, bg=SOFT_YELLOW,
            command=lambda: controller.next_frame("TeacherVerification")
        )
        login_btn.pack(pady=20)

        # Spacer row for vertical centering
        tk.Frame(self, bg=SOFT_BLUE).grid(row=1, column=0)


# Frame 2: Student Selection
class StudentSelectionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_YELLOW)

        title = tk.Label(self, text="Student Selection",
                         font=TITLE_FONT, bg=SOFT_YELLOW, fg=DARK_TEXT)
        title.pack(pady=20)

        # Dropdown Label
        tk.Label(self, text="Select a Student:", font=FONT,
                 bg=SOFT_YELLOW, fg=DARK_TEXT).pack()

        # Student Dropdown
        students = ["Alice", "Bob", "Charlie", "Diana"]
        selected_student = tk.StringVar(value=students[0])
        dropdown = ttk.Combobox(
            self, textvariable=selected_student, values=students, font=FONT)
        dropdown.pack(pady=10)

        # Confirm Button
        confirm_btn = tk.Button(
            self, text="Confirm Selection", font=FONT, bg=SOFT_GREEN, command=lambda: controller.next_frame("StudentSelection")
        )
        confirm_btn.pack(pady=20)




class StorytellingEmotionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_PINK)

        title = tk.Label(self, text="Storytelling Session",
                         font=TITLE_FONT, bg=SOFT_PINK, fg=DARK_TEXT)
        title.pack(pady=20)

        # Placeholder for Story Image
        story_canvas = tk.Canvas(self, width=650, height=430, bg=WHITE)
        story_canvas.pack(pady=5)

        # # Video Feed in Top Right Corner
        # self.cap = cv2.VideoCapture(0)  # Open the default camera
        # video_frame = tk.LabelFrame(self, text="Video Feed", font=FONT, bg=WHITE, fg=DARK_TEXT, labelanchor="n")
        # video_frame.place(relx=0.7, rely=0.05, width=200, height=150)  # Adjusted relx and rely

        # self.video_label = tk.Label(video_frame, bg=WHITE)
        # self.video_label.pack(expand=True, fill="both")
        # self.update_video_feed()

        video_frame = tk.LabelFrame(
            self, text="Video Feed", font=FONT, bg=WHITE, fg=DARK_TEXT, labelanchor="n")
        video_frame.place(relx=0.7, rely=0.05, width=250, height=150)
        video_placeholder = tk.Label(video_frame, text="Video Feed Here", font=(
            "Arial", 10), bg=WHITE, fg=DARK_TEXT)
        video_placeholder.pack(expand=True, fill="both")

        # Control Buttons
        controls_frame = tk.Frame(self, bg=SOFT_PINK)
        controls_frame.pack(pady=20)

        pause_btn = tk.Button(
            controls_frame, text="Pause", font=FONT, bg=SOFT_BLUE, command=lambda: print("Paused")
        )
        pause_btn.pack(side="left", padx=10)

        next_btn = tk.Button(
            controls_frame, text="End", font=FONT, bg=SOFT_BLUE, command=lambda: controller.next_frame("Storytelling")
        )
        next_btn.pack(side="left", padx=10)

    def update_video_feed(self):
        """Update video feed in the video label."""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (200, 150))
            img = ImageTk.PhotoImage(Image.fromarray(frame))
            self.video_label.config(image=img)
            self.video_label.image = img
        self.after(10, self.update_video_feed)  # Refresh every 10 ms

    def __del__(self):
        """Release the video capture when the frame is destroyed."""
        if self.cap.isOpened():
            self.cap.release()


# Frame 4: End of Session
class EndSessionFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=SOFT_YELLOW)

        title = tk.Label(self, text="Session Ended",
                         font=TITLE_FONT, bg=SOFT_YELLOW, fg=DARK_TEXT)
        title.pack(pady=20)

        # Thank you message
        tk.Label(self, text="Thank you for the session!", font=FONT,
                 bg=SOFT_YELLOW, fg=DARK_TEXT).pack(pady=10)

        # View Report Button
        report_btn = tk.Button(
            self, text="View Session Report", font=FONT, bg=SOFT_BLUE, command=lambda: messagebox.showinfo("Report", "Report opened!")
        )
        report_btn.pack(pady=20)


# Main Application Loop
if __name__ == "__main__":
    app = App()
    app.mainloop()
