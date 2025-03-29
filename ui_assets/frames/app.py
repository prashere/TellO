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

    def run_storytelling(self, storytelling_frame):
        """Runs the RL-driven storytelling process inside the UI frame."""

        # Tracking storage
        all_states = []  # Store all states till the end
        total_prompts_given = 0
        total_prompts_answered = 0

        # 1. Greeting & Self-Introduction
        greeting_prompt = self.prompt_manager.get_random_prompt("Greeting")
        speak_text(
            greeting_prompt["text"] if greeting_prompt else "Hello, welcome to TellO!")

        intro_prompt = self.prompt_manager.get_random_prompt(
            "Tello Introduction")
        speak_text(
            intro_prompt["text"] if intro_prompt else "I am TellO, your friendly storytelling robot.")

        storytelling_frame.load_story_image(
            "ui_assets/Images/py_img/teacher.png")
        time.sleep(1)

        # 2. Initial Interaction: Ask the child how they are
        intro_interaction_prompt = self.prompt_manager.get_random_prompt(
            "Getting to Know You")
        speak_text(
            intro_interaction_prompt["text"] if intro_interaction_prompt else "Hello, how are you? What is your name?")

        total_prompts_given += 1  # Tracking prompt count
        initial_response = listen_for_child_response(timeout=10)

        if initial_response.strip():
            total_prompts_answered += 1  # Tracking answered prompt count

        current_state = self.state_updater.update_state_from_story(
            Mode.INTERACTION, initial_response)
        all_states.append(current_state)  # Store state history

        # Encouragement after response
        encouragement_prompt = self.prompt_manager.get_random_prompt(
            "Encouragement")
        speak_text(
            encouragement_prompt["text"] if encouragement_prompt else "Alright, that's good.")
        time.sleep(1)

        # 3. Inform about the Story
        speak_text("Now I will tell you a story.")
        time.sleep(1)

        # 4. Storytelling Loop
        sentence = self.story.start_story()  # Start story
        while sentence:  # Keep looping while sentences are available

            # Update state from sensor data
            horizontal, vertical = storytelling_frame.get_head_pose()
            gaze = storytelling_frame.get_gaze()
            emotion_idx, emotion_conf = storytelling_frame.get_emotion()
            self.state_updater.add_reading(
                horizontal, vertical, gaze, emotion_idx, emotion_conf)

            # Store state
            all_states.append(self.state_updater.get_current_state())

            # Update the image in UI (if available)
            image_file = self.story.get_current_image()
            if image_file:
                storytelling_frame.load_story_image(
                    "dataset/story_corpus/img/" + image_file)

            # Narrate the sentence
            speak_text(sentence["Text"])
            time.sleep(1)

            # *** RL Decision: What to do next? ***
            chosen_action = self.q_learning_agent.get_best_action(
                current_state)

            if chosen_action.action_type == "No-Intervention":
                print("RL Decision: Continue narration.")

            elif chosen_action.action_type == "Clarification":
                speak_text("Do you understand this part?")
                total_prompts_given += 1

                child_response = listen_for_child_response(timeout=10)

                if child_response.strip():
                    total_prompts_answered += 1

                current_state = self.state_updater.update_state_from_story(
                    Mode.INTERACTION, child_response)
                all_states.append(current_state)

            elif chosen_action.action_type == "Lexical-Syntactic":
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

                        child_response = listen_for_child_response(timeout=10)

                        if child_response.strip():
                            total_prompts_answered += 1

                        current_state = self.state_updater.update_state_from_story(
                            Mode.INTERACTION, child_response)
                        all_states.append(current_state)

            # Update Q-table based on reward
            reward = self.environment.get_reward(current_state, chosen_action)
            self.q_learning_agent.update_q_value(
                current_state, chosen_action, reward, current_state)

            # **FIXED: Always move to the next sentence**
            sentence = self.story.get_next_sentence()

        # 5. Before Closure: Ask for Child's Understanding
        speak_text("Can you tell me what you understood about the story?")

        # Stop listening after 3 long silences (10 seconds each)
        max_silence_repeats = 3
        silence_count = 0
        start_time = time.time()  # Track total listening time
        listening_duration = 120  # Max listening time: 2 minutes
        final_understanding = []

        while time.time() - start_time < listening_duration:
            response = listen_for_child_response(timeout=10)

            if not response.strip():
                silence_count += 1
                if silence_count >= max_silence_repeats:
                    speak_text("I didn't hear anything, let's continue.")
                    break
                else:
                    speak_text("C'mon, you can do it!")
            else:
                silence_count = 0
                words = response.split()

                if len(words) < 3:
                    speak_text("Okay, I see. Please continue.")
                else:
                    final_understanding.append(response)

        final_understanding_text = " ".join(final_understanding)
        print("Child's understanding:", final_understanding_text)

        # Store final state
        all_states.append(self.state_updater.get_current_state())

        # 6. Closure
        closure_prompt = self.prompt_manager.get_random_prompt("Closure")
        speak_text(
            closure_prompt["text"] if closure_prompt else "Goodbye! See you next time!")

        # Final state update
        horizontal, vertical = storytelling_frame.get_head_pose()
        gaze = storytelling_frame.get_gaze()
        emotion_idx, emotion_conf = storytelling_frame.get_emotion()
        self.state_updater.add_reading(
            horizontal, vertical, gaze, emotion_idx, emotion_conf)

        all_states.append(self.state_updater.get_current_state())

        storytelling_frame.end_storytelling()

        evaluation_report = self.evaluator.evaluate(
            final_understanding_text,
            all_states,
            prompts_given=total_prompts_given,
            prompts_answered=total_prompts_answered)

        # Save the session data to the database
        if not hasattr(self, 'session_id') or not self.session_id:
            print("Error: Session ID not found. Report not saved.")
            return

        # Prepare API data
        # Update if using a different port
        api_url = "http://127.0.0.1:8000/api/create-student-report/"
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

        # Print Evaluation Summary
        print("\n📊 Evaluation Report:")
        print(
            f"🟢 Vocabulary Score: {evaluation_report['vocabulary'] * 100:.2f}%")
        print(
            f"📖 Structure Similarity Score: {evaluation_report['structure'] * 100:.2f}%")
        print(
            f"✍️ Response Length Score: {evaluation_report['length'] * 100:.2f}%")
        print(
            f"📈 Average Engagement: {evaluation_report['average_engagement']:.2f}")
        print(f"🏆 Final Score: {evaluation_report['final_score']:.2f}%")
        print(
            f"📊 Prompt Interaction Ratio: {evaluation_report['prompt_interaction_ratio']}%")
        print(
            f"📌 Mode Counts: {evaluation_report['state_summary']['mode_counts']}")

        print("\n✅ Session Data Successfully Evaluated.\n")

        # Print statistics
        print("\n--- Storytelling Summary ---")
        print("Total prompts given:", total_prompts_given)
        print("Total prompts answered:", total_prompts_answered)
        print("Final Understanding:", final_understanding_text)
        print("Final States Recorded:", len(all_states))
        print("....................................")
        for state in all_states:
            print(state)
