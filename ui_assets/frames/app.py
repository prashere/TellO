import random
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

from detector_model.state_updater import StateUpdater
from rl_framework.state import EngagementLevel, Mode, PromptNecessity

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

        self.state_updater = StateUpdater(update_interval=2)

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

    # def run_storytelling(self, storytelling_frame):
    #     """Runs the RL-driven storytelling process inside the UI frame."""

    #     # 1. Greeting & Self-Introduction
    #     greeting_prompt = self.prompt_manager.get_random_prompt("Greeting")
    #     greeting_text = greeting_prompt["text"] if greeting_prompt else "Hello, welcome to TellO!"
    #     speak_text(greeting_text)

    #     # Self-introduction using the correct prompt category
    #     intro_prompt = self.prompt_manager.get_random_prompt(
    #         "Tello Introduction")
    #     intro_text = intro_prompt["text"] if intro_prompt else "I am TellO, your friendly storytelling robot."
    #     speak_text(intro_text)

    #     storytelling_frame.load_story_image(
    #         "ui_assets/Images/py_img/teacher.png")  # Default start image
    #     time.sleep(1)

    #     # 2. Initial Interaction: Ask the child how they are and their name
    #     intro_interaction_prompt = self.prompt_manager.get_random_prompt(
    #         "Getting to Know You")
    #     intro_interaction_text = intro_interaction_prompt[
    #         "text"] if intro_interaction_prompt else "Hello, how are you? What is your name?"
    #     speak_text(intro_interaction_text)

    #     # Switch mode explicitly to INTERACTION for this prompt
    #     initial_response = listen_for_child_response(timeout=10)
    #     print("Initial interaction response:", initial_response)

    #     # Update state based on this initial interaction
    #     initial_state = self.state_updater.update_state_from_story(
    #         Mode.INTERACTION, initial_response)
    #     print("State after initial interaction:", initial_state)

    #     # Encouragement after response
    #     encouragement_prompt = self.prompt_manager.get_random_prompt(
    #         "Encouragement")
    #     encouragement_text = encouragement_prompt["text"] if encouragement_prompt else "Alright, that's good."
    #     speak_text(encouragement_text)
    #     time.sleep(1)

    #     # 3. Inform about the Story
    #     speak_text("Now I will tell you a story.")
    #     time.sleep(1)

    #     # 4. Storytelling Loop
    #     sentence = self.story.start_story()
    #     sentence_count = 0
    #     current_state = initial_state  # Start with state from initial interaction

    #     while sentence:
    #         sentence_count += 1

    #         # Update the state from sensor data after each sentence
    #         horizontal, vertical = storytelling_frame.get_head_pose()
    #         gaze = storytelling_frame.get_gaze()
    #         emotion_idx, emotion_conf = storytelling_frame.get_emotion()

    #         self.state_updater.add_reading(
    #             horizontal, vertical, gaze, emotion_idx, emotion_conf)
    #         updated_state = self.state_updater.maybe_update()
    #         if updated_state is not None:
    #             current_state = updated_state
    #             print("Aggregated State after sentence:", current_state)

    #         # Update the image in UI (if available)
    #         image_file = self.story.get_current_image()
    #         if image_file:
    #             storytelling_frame.load_story_image(
    #                 "dataset/story_corpus/img/" + image_file)

    #         # Narrate the sentence
    #         speak_text(sentence["Text"])
    #         time.sleep(1)

    #         # Interaction Prompt every 2 sentences
    #         if sentence_count % 2 == 0:
    #             fun_questions = sentence.get("FunQuestions", [])
    #             if fun_questions:
    #                 # Choose a random fun question
    #                 fun_question = random.choice(fun_questions)
    #                 speak_text(fun_question)
    #             else:
    #                 interaction_prompt = sentence.get(
    #                     "InteractionPrompt", "What do you see in the picture?")
    #                 speak_text(interaction_prompt)

    #             # Explicitly set mode to INTERACTION for the prompt phase
    #             current_state.mode = Mode.INTERACTION
    #             child_response = listen_for_child_response(timeout=10)
    #             print("Child's response:", child_response)

    #             # Update state based on child's interaction response
    #             new_state = self.state_updater.update_state_from_story(
    #                 Mode.INTERACTION,
    #                 child_response)
    #             if new_state is not None:
    #                 current_state = new_state
    #                 print("Updated State after interaction:", current_state)

    #             # Encouragement after response
    #             encouragement_prompt = self.prompt_manager.get_random_prompt(
    #                 "Encouragement")
    #             encouragement_text = encouragement_prompt[
    #                 "text"] if encouragement_prompt else "Alright, that's good."
    #             speak_text(encouragement_text)
    #             time.sleep(1)

    #         # Get the next sentence
    #         sentence = self.story.get_next_sentence()

    #     # 5. End Storytelling
    #     closure_prompt = self.prompt_manager.get_random_prompt("Closure")
    #     closure_text = closure_prompt["text"] if closure_prompt else "Goodbye! See you next time!"
    #     speak_text(closure_text)

    #     # Update state one last time (for closure)
    #     horizontal, vertical = storytelling_frame.get_head_pose()
    #     gaze = storytelling_frame.get_gaze()
    #     emotion_idx, emotion_conf = storytelling_frame.get_emotion()

    #     self.state_updater.add_reading(
    #         horizontal, vertical, gaze, emotion_idx, emotion_conf)
    #     final_state = self.state_updater.maybe_update()
    #     if final_state is not None:
    #         print("Final Aggregated State:", final_state)

    #     # Move to the next UI frame
    #     storytelling_frame.end_storytelling()

    def run_storytelling(self, storytelling_frame):
        """Runs the RL-driven storytelling process inside the UI frame."""

        # 1. Greeting & Self-Introduction
        greeting_prompt = self.prompt_manager.get_random_prompt("Greeting")
        greeting_text = greeting_prompt["text"] if greeting_prompt else "Hello, welcome to TellO!"
        speak_text(greeting_text)

        # Self-introduction using the correct prompt category
        intro_prompt = self.prompt_manager.get_random_prompt(
            "Tello Introduction")
        intro_text = intro_prompt["text"] if intro_prompt else "I am TellO, your friendly storytelling robot."
        speak_text(intro_text)

        storytelling_frame.load_story_image(
            "ui_assets/Images/py_img/teacher.png")  # Default start image
        time.sleep(1)

        # 2. Initial Interaction: Ask the child how they are and their name
        intro_interaction_prompt = self.prompt_manager.get_random_prompt(
            "Getting to Know You")
        intro_interaction_text = intro_interaction_prompt[
            "text"] if intro_interaction_prompt else "Hello, how are you? What is your name?"
        speak_text(intro_interaction_text)

        # Switch mode explicitly to INTERACTION for this prompt
        initial_response = listen_for_child_response(timeout=10)
        print("Initial interaction response:", initial_response)

        # Update state based on this initial interaction
        initial_state = self.state_updater.update_state_from_story(
            Mode.INTERACTION, initial_response)
        print("State after initial interaction:", initial_state)

        # Encouragement after response
        encouragement_prompt = self.prompt_manager.get_random_prompt(
            "Encouragement")
        encouragement_text = encouragement_prompt["text"] if encouragement_prompt else "Alright, that's good."
        speak_text(encouragement_text)
        time.sleep(1)

        # 3. Inform about the Story
        speak_text("Now I will tell you a story.")
        time.sleep(1)

        # 4. Storytelling Loop
        sentence = self.story.start_story()
        sentence_count = 0
        current_state = initial_state  # Start with state from initial interaction
        last_question = None  # To avoid repetition of fun questions

        while sentence:
            sentence_count += 1

            # Update the state from sensor data after each sentence
            horizontal, vertical = storytelling_frame.get_head_pose()
            gaze = storytelling_frame.get_gaze()
            emotion_idx, emotion_conf = storytelling_frame.get_emotion()

            self.state_updater.add_reading(
                horizontal, vertical, gaze, emotion_idx, emotion_conf)
            updated_state = self.state_updater.maybe_update()
            if updated_state is not None:
                current_state = updated_state
                print("Aggregated State after sentence:", current_state)

            # Update the image in UI (if available)
            image_file = self.story.get_current_image()
            if image_file:
                storytelling_frame.load_story_image(
                    "dataset/story_corpus/img/" + image_file)

            # Narrate the sentence
            speak_text(sentence["Text"])
            time.sleep(1)

            # Interaction Prompt every 2 sentences
            if sentence_count % 2 == 0:
                # First, try using a fun question if available
                fun_questions = sentence.get("FunQuestions", [])
                if fun_questions:
                    available_questions = [
                        q for q in fun_questions if q != last_question]
                    if available_questions:
                        fun_question = random.choice(available_questions)
                    else:
                        fun_question = random.choice(fun_questions)
                    last_question = fun_question
                    speak_text(fun_question)
                else:
                    # Use the default interaction prompt if no fun questions
                    interaction_prompt = sentence.get(
                        "InteractionPrompt", "What do you see in the picture?")
                    last_question = interaction_prompt
                    speak_text(interaction_prompt)

                # Explicitly set mode to INTERACTION for the prompt phase
                current_state.mode = Mode.INTERACTION
                child_response = listen_for_child_response(timeout=10)
                print("Child's response:", child_response)

                # Update state based on child's interaction response
                new_state = self.state_updater.update_state_from_story(
                    Mode.INTERACTION, child_response)
                if new_state is not None:
                    current_state = new_state
                    print("Updated State after interaction:", current_state)

                # Check for WH-Question Handling:
                if current_state.wh_question_detected and current_state.prompt_necessity == PromptNecessity.YES:
                    wh_prompt = self.prompt_manager.get_random_prompt(
                        "WH-Question Handling")
                    wh_text = wh_prompt["text"] if wh_prompt else "Could you please repeat that question?"
                    speak_text(wh_text)
                    # Repeat the same prompt that was previously asked
                    speak_text(last_question)
                    # Listen again for response
                    child_response = listen_for_child_response(timeout=10)
                    print("Child's response after WH-handling:", child_response)
                    # Update state after WH-question handling
                    current_state = self.state_updater.update_state_from_story(
                        Mode.INTERACTION, child_response)
                    print("State after WH-question handling:", current_state)

                # Check for Low Engagement and Prompt Necessity for Motivation:
                if current_state.prompt_necessity == PromptNecessity.YES and current_state.engagement_level == EngagementLevel.LOW:
                    motivation_prompt = self.prompt_manager.get_random_prompt(
                        "Motivation")
                    motivation_text = motivation_prompt["text"] if motivation_prompt else "You're doing great! Keep going!"
                    speak_text(motivation_text)
                    time.sleep(1)
                    # Ask for a new fun question (ensuring it's not the same as last_question)
                    if fun_questions:
                        available_questions = [
                            q for q in fun_questions if q != last_question]
                        if available_questions:
                            new_fun_question = random.choice(
                                available_questions)
                        else:
                            new_fun_question = random.choice(fun_questions)
                        last_question = new_fun_question
                        speak_text(new_fun_question)
                    else:
                        interaction_prompt = sentence.get(
                            "InteractionPrompt", "What do you see in the picture?")
                        last_question = interaction_prompt
                        speak_text(interaction_prompt)
                    # Set mode to INTERACTION and listen for response
                    current_state.mode = Mode.INTERACTION
                    child_response = listen_for_child_response(timeout=10)
                    print("Child's response after motivation:", child_response)
                    current_state = self.state_updater.update_state_from_story(
                        Mode.INTERACTION, child_response)
                    print("State after motivation response:", current_state)
                    time.sleep(1)

                # Encouragement after response
                encouragement_prompt = self.prompt_manager.get_random_prompt(
                    "Encouragement")
                encouragement_text = encouragement_prompt[
                    "text"] if encouragement_prompt else "Alright, that's good."
                speak_text(encouragement_text)
                time.sleep(1)

            # Get the next sentence
            sentence = self.story.get_next_sentence()

        # 5. End Storytelling
        closure_prompt = self.prompt_manager.get_random_prompt("Closure")
        closure_text = closure_prompt["text"] if closure_prompt else "Goodbye! See you next time!"
        speak_text(closure_text)

        # Update state one last time (for closure)
        horizontal, vertical = storytelling_frame.get_head_pose()
        gaze = storytelling_frame.get_gaze()
        emotion_idx, emotion_conf = storytelling_frame.get_emotion()

        self.state_updater.add_reading(
            horizontal, vertical, gaze, emotion_idx, emotion_conf)
        final_state = self.state_updater.maybe_update()
        if final_state is not None:
            print("Final Aggregated State:", final_state)

        # Move to the next UI frame
        storytelling_frame.end_storytelling()
