import tkinter as tk
import json
import time
from PIL import Image, ImageTk
import cv2

# Import UI Frames
from .teacher_verification import TeacherVerificationFrame
from .student_selection import StudentSelectionFrame
from .storytelling_emotion import StorytellingEmotionFrame
from .end_session import EndSessionFrame
from .guidelines import GuidelinesFrame
from .loading import LoadingFrame

# Import Story and Prompts
from story_handler.story import Story
from story_handler.prompt import PromptManager

# Import TTS & STT Functions
# Assuming modularized functions
from .speech_text import speak_text, listen_for_child_response

# Colors and Fonts
SOFT_BLUE = "#add8e6"
WHITE = "#ffffff"


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Child-Friendly Application")
        self.geometry("1000x600")
        self.resizable(False, False)

        # Load Story and Prompts
        with open("dataset/story_corpus/stories/easy/story3.json", "r", encoding="utf-8") as f:
            self.story = Story(json.load(f))

        with open("dataset/prompts.json", "r", encoding="utf-8") as f:
            self.prompt_manager = PromptManager(json.load(f))

        self.frames = {}
        self.current_frame = None

        self.load_images()
        self.create_frames()
        self.show_frame("TeacherVerification")

    def load_images(self):
        """Load and resize images for UI."""
        self.logo_img = ImageTk.PhotoImage(
            Image.open("ui_assets/Images/py_img/teacher.png").resize((300, 220)))
        self.user_icon = ImageTk.PhotoImage(
            Image.open("ui_assets/Images/py_img/user.png").resize((30, 30)))
        self.password_icon = ImageTk.PhotoImage(
            Image.open("ui_assets/Images/py_img/password.png").resize((30, 30)))

    def create_frames(self):
        """Create and initialize UI frames."""
        container = tk.Frame(self, bg=WHITE)
        container.pack(fill="both", expand=True)

        self.frames["TeacherVerification"] = TeacherVerificationFrame(
            container, self)
        self.frames["StudentSelection"] = StudentSelectionFrame(
            container, self)
        self.frames["Storytelling"] = StorytellingEmotionFrame(container, self)
        self.frames["EndSession"] = EndSessionFrame(container, self)
        self.frames["Guidelines"] = GuidelinesFrame(container, self)
        self.frames["Loading"] = LoadingFrame(container, self)

    def show_frame(self, frame_name):
        """Switch between frames and call on_show if available."""
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = self.frames[frame_name]
        self.current_frame.pack(fill="both", expand=True)
        if hasattr(self.current_frame, "on_show"):
            self.current_frame.on_show()

    def next_frame(self, current_frame):
        """Navigate to the next frame."""
        next_frames = {
            "TeacherVerification": "StudentSelection",
            "StudentSelection": "Guidelines",
            "Guidelines": "Loading",
            "Loading": "Storytelling",
            "Storytelling": "EndSession",
            "EndSession": "TeacherVerification",
        }
        self.show_frame(next_frames[current_frame])

    def run_storytelling(self, storytelling_frame):
        """Runs the storytelling process inside the UI frame."""
        # 1. Greeting
        greeting_prompt = self.prompt_manager.get_random_prompt("Greeting")
        greeting_text = greeting_prompt["text"] if greeting_prompt else "Hello, welcome to TellO!"
        speak_text(greeting_text)
        storytelling_frame.load_story_image(
            "ui_assets/Images/py_img/teacher.png")  # Default start image
        time.sleep(1)

        # 2. Inform about the story
        speak_text("Now I will tell you a story.")
        time.sleep(1)

        # 3. Start the story
        sentence = self.story.start_story()
        sentence_count = 0

        while sentence:
            sentence_count += 1

            # Update Image in UI
            image_file = self.story.get_current_image()
            if image_file:
                storytelling_frame.load_story_image(
                    "dataset/story_corpus/img/" + image_file)

            # Speak the sentence
            speak_text(sentence["Text"])
            time.sleep(1)

            # Interaction every 2 sentences
            if sentence_count % 2 == 0:
                interaction_prompt = sentence.get(
                    "InteractionPrompt", "What do you think?")
                speak_text(interaction_prompt)
                child_response = listen_for_child_response(timeout=2)
                print("Child's response:", child_response)
                speak_text("Alright, that's good.")
                time.sleep(1)

            # Get next sentence
            sentence = self.story.get_next_sentence()

        # 4. End storytelling
        closure_prompt = self.prompt_manager.get_random_prompt("Closure")
        closure_text = closure_prompt["text"] if closure_prompt else "Goodbye! See you next time!"
        speak_text(closure_text)

        # Move to the next UI frame
        storytelling_frame.end_storytelling()
