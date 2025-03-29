import random
import tkinter as tk
import json
import time
from PIL import Image, ImageTk
import cv2
import requests

from ui_assets.evaluator import ResponseEvaluator

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

from detector_model.state_updater import StateUpdater

from rl_framework.state import EngagementLevel, Mode, PromptNecessity
from rl_framework.q_learning import QLearning
from rl_framework.constant_actions import get_all_actions
from rl_framework.environment import Environment

# Colors and Fonts
SOFT_BLUE = "#add8e6"
WHITE = "#ffffff"

all_actions = get_all_actions()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Child-Friendly Application")
        self.geometry("1000x600")
        self.resizable(False, False)

        # Load Story and Prompts
        with open("dataset/story_corpus/stories/easy/story4.json", "r", encoding="utf-8") as f:
            self.story = Story(json.load(f))

        with open("dataset/prompts.json", "r", encoding="utf-8") as f:
            self.prompt_manager = PromptManager(json.load(f))

        self.frames = {}
        self.current_frame = None

        self.load_images()
        self.create_frames()
        self.show_frame("TeacherVerification")

        self.state_updater = StateUpdater(update_interval=2)

        self.q_learning_agent = QLearning(all_actions)
        self.environment = Environment(self.q_learning_agent)
        self.q_learning_agent.load_q_table()
        self.evaluator = ResponseEvaluator(self.story)

        self.selected_student_id = None
        self.story_id = None
        self.session_start_time = None
        self.session_id = None

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

    def update_storytelling_state(self, detected_state):
        """Update state in response to detected emotions, gaze, and head pose."""
        # print("Updated Storytelling State:", detected_state)
        # Here, you can use `detected_state` to update a state manager, log data, or adjust the RL system.

    # ..................................................................................
    # Storytelling Process
    # ..................................................................................
    def run_storytelling(self, storytelling_frame):
        """Runs the RL-driven storytelling process inside the UI frame."""

        # Initialize tracking variables
        all_states = []
        total_prompts_given = 0
        total_prompts_answered = 0

        # Step 1: Greeting & Introduction
        self.perform_greeting()

        # Step 2: Initial Interaction with the child
        total_prompts_given, total_prompts_answered = self.initial_interaction(
            storytelling_frame, total_prompts_given, total_prompts_answered, all_states)

        # Step 3: Inform about the story and start storytelling loop
        speak_text("Now I will tell you a story.")
        time.sleep(1)
        self.storytelling_loop(
            storytelling_frame, all_states, total_prompts_given, total_prompts_answered)

        # Step 4: Ask for Child's Understanding
        final_understanding_text = self.collect_child_understanding()

        # Step 5: Closure
        self.perform_closure(storytelling_frame, all_states)

        # Step 6: Generate and Save Evaluation Report
        self.generate_and_save_report(
            final_understanding_text, all_states, total_prompts_given, total_prompts_answered)

    def perform_greeting(self):
        """Handles greeting and introduction."""
        greeting_prompt = self.prompt_manager.get_random_prompt("Greeting")
        speak_text(
            greeting_prompt["text"] if greeting_prompt else "Hello, welcome to TellO!")

        intro_prompt = self.prompt_manager.get_random_prompt(
            "Tello Introduction")
        speak_text(
            intro_prompt["text"] if intro_prompt else "I am TellO, your friendly storytelling robot.")

    def initial_interaction(self, storytelling_frame, total_prompts_given, total_prompts_answered, all_states):
        """Initial interaction where TellO asks for the child's name and how they are."""
        storytelling_frame.load_story_image(
            "ui_assets/Images/py_img/teacher.png")
        time.sleep(1)

        intro_interaction_prompt = self.prompt_manager.get_random_prompt(
            "Getting to Know You")
        speak_text(
            intro_interaction_prompt["text"] if intro_interaction_prompt else "Hello, how are you? What is your name?")

        total_prompts_given += 1
        initial_response = listen_for_child_response(timeout=10)

        if initial_response.strip():
            total_prompts_answered += 1

        current_state = self.state_updater.update_state_from_story(
            Mode.INTERACTION, initial_response)
        all_states.append(current_state)

        encouragement_prompt = self.prompt_manager.get_random_prompt(
            "Encouragement")
        speak_text(
            encouragement_prompt["text"] if encouragement_prompt else "Alright, that's good.")
        time.sleep(1)

        return total_prompts_given, total_prompts_answered

    def storytelling_loop(self, storytelling_frame, all_states, total_prompts_given, total_prompts_answered):
        """Handles the storytelling loop with RL-driven decisions."""
        sentence = self.story.start_story()

        while sentence:
            # Update engagement state
            self.update_engagement_state(storytelling_frame, all_states)

            # Update UI with image
            self.update_story_image(storytelling_frame)

            # Narrate the sentence
            speak_text(sentence["Text"])
            time.sleep(1)

            # RL-based decision-making
            total_prompts_given, total_prompts_answered = self.handle_rl_decision(
                storytelling_frame, all_states, total_prompts_given, total_prompts_answered)

            # Move to the next sentence
            sentence = self.story.get_next_sentence()

    def update_engagement_state(self, storytelling_frame, all_states):
        """Updates the state based on head pose, gaze, and emotions."""
        horizontal, vertical = storytelling_frame.get_head_pose()
        gaze = storytelling_frame.get_gaze()
        emotion_idx, emotion_conf = storytelling_frame.get_emotion()

        self.state_updater.add_reading(
            horizontal, vertical, gaze, emotion_idx, emotion_conf)
        all_states.append(self.state_updater.get_current_state())

    def update_story_image(self, storytelling_frame):
        """Updates the UI with the current story image."""
        image_file = self.story.get_current_image()
        if image_file:
            storytelling_frame.load_story_image(
                "dataset/story_corpus/img/" + image_file)

    def handle_rl_decision(self, storytelling_frame, all_states, total_prompts_given, total_prompts_answered):
        """Handles RL-based decision making for interaction."""
        current_state = self.state_updater.get_current_state()
        chosen_action = self.q_learning_agent.get_best_action(current_state)

        if chosen_action.action_type == "No-Intervention":
            print("RL Decision: Continue narration.")

        elif chosen_action.action_type == "Clarification":
            total_prompts_given += 1
            speak_text("Do you understand this part?")
            response = listen_for_child_response(timeout=10)

            if response.strip():
                total_prompts_answered += 1

            self.update_interaction_state(response, all_states)

        elif chosen_action.action_type == "Lexical-Syntactic":
            total_prompts_given, total_prompts_answered = self.handle_lexical_syntactic_action(
                all_states, total_prompts_given, total_prompts_answered)

        return total_prompts_given, total_prompts_answered

    def handle_lexical_syntactic_action(self, all_states, total_prompts_given, total_prompts_answered):
        """Handles vocabulary explanations and fun questions."""
        vocab_present, word, definition = self.story.get_vocabulary_info()

        if vocab_present:
            speak_text(
                f"Let me tell you the meaning of the word '{word}'. It means {definition}.")
        else:
            fun_questions = self.story.get_fun_questions()
            if fun_questions:
                selected_question = random.choice(fun_questions)
                speak_text(selected_question)
                total_prompts_given += 1

                response = listen_for_child_response(timeout=10)
                if response.strip():
                    total_prompts_answered += 1

                self.update_interaction_state(response, all_states)

        return total_prompts_given, total_prompts_answered

    def collect_child_understanding(self):
        """Collects the final understanding of the child after storytelling."""
        speak_text("Can you tell me what you understood about the story?")

        silence_count = 0
        final_understanding = []
        start_time = time.time()
        max_listening_time = 120

        while time.time() - start_time < max_listening_time:
            response = listen_for_child_response(timeout=10)

            if not response.strip():
                silence_count += 1
                if silence_count >= 3:
                    speak_text("I didn't hear anything, let's continue.")
                    break
                else:
                    speak_text("C'mon, you can do it!")
            else:
                silence_count = 0
                words = response.split()
                if len(words) >= 3:
                    final_understanding.append(response)

        return " ".join(final_understanding)

    def perform_closure(self, storytelling_frame, all_states):
        """Handles the closure of the storytelling session."""
        closure_prompt = self.prompt_manager.get_random_prompt("Closure")
        speak_text(
            closure_prompt["text"] if closure_prompt else "Goodbye! See you next time!")

        self.update_engagement_state(storytelling_frame, all_states)
        storytelling_frame.end_storytelling()

    def generate_and_save_report(self, final_understanding_text, all_states, total_prompts_given, total_prompts_answered):
        """Generates the evaluation report and saves it."""
        evaluation_report = self.evaluator.evaluate(
            final_understanding_text, all_states, total_prompts_given, total_prompts_answered)

        self.save_report_to_db(evaluation_report, total_prompts_answered)
        # self.print_evaluation_summary(evaluation_report)

    def update_interaction_state(self, response, all_states):
        """Updates the state based on the child's response."""
        current_state = self.state_updater.update_state_from_story(
            Mode.INTERACTION, response)
        all_states.append(current_state)  # Store the updated state
        return current_state

    def save_report_to_db(self, evaluation_report, total_prompts_answered):
        """Saves the evaluation report to the database via an API request."""

        if not hasattr(self, 'session_id') or not self.session_id:
            print("Error: Session ID not found. Report not saved.")
            return

        # API URL (update if needed)
        api_url = "http://127.0.0.1:8000/api/create-student-report/"

        # Prepare report data
        report_data = {
            "session_id": self.session_id,
            "vocab_score": evaluation_report["vocabulary"],
            "structure_sim_score": evaluation_report["structure"],
            "response_length": evaluation_report["length"],
            "avg_engagement": evaluation_report["average_engagement"],
            "final_score": evaluation_report["final_score"],
            "prompt_interaction_ratio": evaluation_report["prompt_interaction_ratio"],
            "prompt_interaction_count": total_prompts_answered,
            "feedback_notes": "Automatically generated report"
        }

        try:
            response = requests.post(api_url, json=report_data)
            response_data = response.json()

            if response.status_code == 201:
                print(
                    f"Report successfully saved! Report ID: {response_data['report_id']}")
            else:
                print(f"Error saving report: {response_data}")

        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {str(e)}")
