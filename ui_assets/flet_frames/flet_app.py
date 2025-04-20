import threading
import flet as ft
import requests
import time
import random
import json

from .login import build_teacher_verification_frame
from .std_selection import build_student_selection_frame
from .instructions import build_guidelines_frame as guidelines_frame_external
from .instructions import build_loading_frame as loading_frame_external
from .storytelling import build_storytelling_frame
from .end import build_end_session_frame

from story_handler.story import Story
from story_handler.prompt import PromptManager

from rl_framework.state import EngagementLevel, Mode, PromptNecessity
from rl_framework.q_learning import QLearning
from rl_framework.constant_actions import get_all_actions
from rl_framework.environment import Environment
from .speech_text import listen_for_child_response
from .triall import speak_text

from ui_assets.evaluator import ResponseEvaluator
from detector_model.state_updater import StateUpdater
from serial_communication.robot_comm import execute_combo, init_serial


def speak_and_execute_async(text, combo_name, ser):
        # threading.Thread(target=speak_text, args=(text,), daemon=True).start()
        # threading.Thread(target=execute_combo, args=(ser, combo_name), daemon=True).start()
        t_speech = threading.Thread(target=speak_text, args=(text,))
        # Thread for servo+expression combo
        t_combo = threading.Thread(target=execute_combo, args=(ser, combo_name))
    
        # start both
        t_speech.start()
        t_combo.start()
    
        # (optionally) wait for both to finish
        t_speech.join()
        t_combo.join()

class MyApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.frames = {}
        self.current_frame = None
        self.teacher_id = None
        self.username = None
        self.create_frames()
        all_actions = get_all_actions()

        # Load Story and Prompts
        with open("dataset/story_corpus/stories/easy/story3.json", "r", encoding="utf-8") as f:
            self.story = Story(json.load(f))

        with open("dataset/prompts.json", "r", encoding="utf-8") as f:
            self.prompt_manager = PromptManager(json.load(f))

        self.state_updater = StateUpdater(update_interval=2)

        self.q_learning_agent = QLearning(all_actions)
        self.environment = Environment(self.q_learning_agent)
        self.q_learning_agent.load_q_table()
        self.evaluator = ResponseEvaluator(self.story)

        self.student_name_id_map = None
        self.selected_student_id = None
        self.story_id = None
        self.session_start_time = None
        self.session_id = None
        self.state = "idle"
        self.serial_conn = init_serial()


    def create_frames(self):
        self.frames["TeacherVerification"] = build_teacher_verification_frame(
            self)
        self.frames["StudentSelection"] = build_student_selection_frame(self)
        self.frames["Guidelines"] = self.build_guidelines_frame()
        self.frames["Loading"] = self.build_loading_frame()
        self.frames["Storytelling"] = build_storytelling_frame(self)
        self.frames["EndSession"] = build_end_session_frame(self)
        self.stack = ft.Stack(controls=list(self.frames.values()), expand=True)
        self.page.add(self.stack)
        self.show_frame("TeacherVerification")

    def show_frame(self, frame_name):
        for name, frame in self.frames.items():
            frame.visible = (name == frame_name)
        self.current_frame = frame_name
        self.page.update()
        frame_obj = self.frames[frame_name]
        if hasattr(frame_obj, "on_mount") and callable(getattr(frame_obj, "on_mount", None)):
            frame_obj.on_mount()
        if hasattr(frame_obj, "on_show") and callable(getattr(frame_obj, "on_show", None)):
            frame_obj.on_show()

    def next_frame(self):
        next_frames = {
            "TeacherVerification": "StudentSelection",
            "StudentSelection": "Guidelines",
            "Guidelines": "Loading",
            "Loading": "Storytelling",
            "Storytelling": "EndSession",
            "EndSession": "TeacherVerification",
        }
        next_frame_name = next_frames.get(self.current_frame)
        if next_frame_name:
            self.show_frame(next_frame_name)

    def build_student_selection_frame(self):
        return ft.Container(ft.Text("Student Selection Page"), visible=False)

    def build_guidelines_frame(self):
        return guidelines_frame_external(self)

    def build_loading_frame(self):
        temp = loading_frame_external(self)
        self.next_frame()
        return temp
    
    


    def run_storytelling(self, storytelling_frame):
        """Runs the RL-driven storytelling process inside the UI frame."""

        # Initialize tracking variables
        all_states = []
        total_prompts_given = 0
        total_prompts_answered = 0

        storytelling_frame.load_story_image(
            "ui_assets/Images/py_img/robot_hello.jpg")
        time.sleep(1)

        # Step 1: Greeting & Introduction
        self.perform_greeting()

        # Step 2: Initial Interaction with the child
        total_prompts_given, total_prompts_answered = self.initial_interaction(
            storytelling_frame, total_prompts_given, total_prompts_answered, all_states)

        # Step 3: Inform about the story and start storytelling loop
        text = "Now I will tell you a story."
        speak_and_execute_async(text, "intro", self.serial_conn)
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
        greeting_prompt = self.prompt_manager.get_random_prompt("Greeting")
        # Queue the greeting and get its event
        text = greeting_prompt["text"] if greeting_prompt else "Hello, welcome to TellO!"
        # speak_text(greeting_prompt["text"] if greeting_prompt else "Hello, welcome to TellO!")
        # execute_combo(self.serial_conn, "intro")
        speak_and_execute_async(text, "intro", self.serial_conn)
        # Wait until the greeting is spoken before proceeding.

        intro_prompt = self.prompt_manager.get_random_prompt(
            "Tello Introduction")
        # Queue the introduction and get its event
        # speak_text(intro_prompt["text"] if intro_prompt else "I am TellO, your friendly storytelling robot.")
        text = intro_prompt["text"] if intro_prompt else "I am TellO, your friendly storytelling robot."
        speak_and_execute_async(text, "prompt", self.serial_conn)
        # Wait until the introduction is spoken.

    def initial_interaction(self, storytelling_frame, total_prompts_given, total_prompts_answered, all_states):
        print("Inside getting to know you")
        """Initial interaction where TellO asks for the child's name and how they are."""

        intro_interaction_prompt = self.prompt_manager.get_random_prompt(
            "Getting to Know You")
        # execute_combo(self.serial_conn, "disagree")
        # speak_text(intro_interaction_prompt["text"] if intro_interaction_prompt else "Hello, how are you? What is your name?")
        speak_and_execute_async(intro_interaction_prompt, "disagree", self.serial_conn)
        self.state = "listening"
        execute_combo(self.serial_conn, "listening")
        total_prompts_given += 1
        initial_response = listen_for_child_response(timeout=10)
        self.state = "idle"
        count = 0

        # Reprompt if no response initially
        while not initial_response.strip() and count < 1:
            # speak_text("I didn't hear you, please say it again.")
            text = "I didn't hear you, please say it again."
            speak_and_execute_async(text, "listening", self.serial_conn)
            self.state = "listening"
            initial_response = listen_for_child_response(timeout=10)
            self.state = "idle"
            count += 1

        if initial_response.strip():
            total_prompts_answered += 1
            current_state = self.state_updater.update_state_from_story(
                Mode.INTERACTION, initial_response)
            all_states.append(current_state)

            encouragement_prompt = self.prompt_manager.get_random_prompt(
                "Encouragement")
            # execute_combo(self.serial_conn, "encouragement")
            # speak_text(encouragement_prompt["text"] if encouragement_prompt else "Alright, that's good.")
            text = encouragement_prompt["text"] if encouragement_prompt else "Alright, that's good."
            speak_and_execute_async(text, "encouragement", self.serial_conn)
            
        else:
            # execute_combo(self.serial_conn, "encouragement")
            # speak_text("That's okay, let's move forward together!")
            text = "That's okay, let's move forward together!"
            speak_and_execute_async(text, "encouragement", self.serial_conn)
            current_state = self.state_updater.update_state_from_story(
                Mode.NARRATION, "")
            all_states.append(current_state)

        execute_combo(self.serial_conn, "narration")
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
            current_sentence = sentence["Text"]
            time.sleep(1)

            # RL-based decision-making
            total_prompts_given, total_prompts_answered = self.handle_rl_decision(
                storytelling_frame, all_states, total_prompts_given, total_prompts_answered, current_sentence)

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

    def handle_rl_decision(self, storytelling_frame, all_states, total_prompts_given, total_prompts_answered, current_sentence):
        """Handles RL-based decision making for interaction."""
        current_state = self.state_updater.get_current_state()
        chosen_action = self.q_learning_agent.get_best_action(current_state)

        if chosen_action.action_type == "No-Intervention":
            print("RL Decision: Continue narration.")

        elif chosen_action.action_type == "Clarification":
            total_prompts_given += 1
            # execute_combo(self.serial_conn, "agree")
            # speak_text("Do you understand this part?")
            text = "Do you understand this part?"
            speak_and_execute_async(text, "agree", self.serial_conn)
            self.state = "listening"
            response = listen_for_child_response(timeout=10)
            self.state = "idle"

            if response.strip():
                total_prompts_answered += 1
                response_lower = response.strip().lower()

                # Check for negative/confused responses
                negative_keywords = ["no", "none", "i don't",
                                     "not really", "don't understand", "confused"]
                if any(neg in response_lower for neg in negative_keywords):
                    # execute_combo(self.serial_conn, "motivation")
                    # speak_text("No worries, let me repeat that part.")
                    # execute_combo(self.serial_conn, "narration")
                    text = "No worries, let me repeat that part."
                    speak_and_execute_async(text, "motivation", self.serial_conn)
                    # speak_text(current_sentence)
                    speak_and_execute_async(current_sentence, "narration", self.serial_conn)
                    
                else:
                    # execute_combo(self.serial_conn, "encouragement")
                    # speak_text("Great! Let's continue.")
                    text = "Great! Let's continue."
                    speak_and_execute_async(text, "encouragement", self.serial_conn)
            else:
                # execute_combo(self.serial_conn, "motivation")
                # speak_text("Okay, let's move to the next part.")
                text = "Okay, let's move to the next part."
                speak_and_execute_async(text, "motivation", self.serial_conn)

            execute_combo(self.serial_conn, "narration")
            self.update_interaction_state(response, all_states)

        elif chosen_action.action_type == "Lexical-Syntactic":
            total_prompts_given, total_prompts_answered = self.handle_lexical_syntactic_action(
                all_states, total_prompts_given, total_prompts_answered)

        return total_prompts_given, total_prompts_answered

    def handle_lexical_syntactic_action(self, all_states, total_prompts_given, total_prompts_answered):
        """Handles vocabulary explanations and fun questions while preventing duplicate word definitions."""

        # Retrieve the vocabulary word from the current sentence
        vocab_present, word, definition = self.story.get_vocabulary_info()

        # Ensure explained_words set exists in the session
        if not hasattr(self, "explained_words"):
            self.explained_words = set()

        if vocab_present and word not in self.explained_words:
            # Explain the word only if it hasn't been explained before
            # speak_text(f"Let me tell you the meaning of the word '{word}'. It means {definition}.")
            text = f"Let me tell you the meaning of the word '{word}'. It means {definition}."
            speak_and_execute_async(text, "prompt", self.serial_conn)
            self.explained_words.add(word)  # Mark word as explained
        else:
            # Proceed to fun questions if no new vocab word to explain
            fun_questions = self.story.get_fun_questions()
            if fun_questions:
                selected_question = random.choice(fun_questions)
                # execute_combo(self.serial_conn, "prompt")
                # speak_text(selected_question)
                speak_and_execute_async(selected_question, "prompt", self.serial_conn)
                self.state = "listening"
                total_prompts_given += 1

                response = listen_for_child_response(timeout=10)
                self.state = "idle"
                count = 0
                while not response.strip() and count < 1:
                    # execute_combo(self.serial_conn, "listening")
                    # speak_text("I didn't hear you, please say it again.")
                    text = "I didn't hear you, please say it again."
                    speak_and_execute_async(text, "listening", self.serial_conn)
                    self.state = "listening"
                    response = listen_for_child_response(timeout=10)
                    self.state = "idle"
                    count += 1

                if response.strip():
                    total_prompts_answered += 1
                    self.state = "idle"
                    # execute_combo(self.serial_conn, "encouragement")
                    # speak_text(self.prompt_manager.get_random_prompt("Encouragement")["text"] if self.prompt_manager.get_random_prompt("Encouragement") else "That's great!")
                    text = self.prompt_manager.get_random_prompt("Encouragement")["text"] if self.prompt_manager.get_random_prompt("Encouragement") else "That's great!"
                    speak_and_execute_async(text, "encouragement", self.serial_conn)
                if count == 1:
                    # execute_combo(self.serial_conn, "disagree")
                    # speak_text("Okay, let's move on to the next part of the story.")
                    text = "Okay, let's move on to the next part of the story."
                    speak_and_execute_async(text, "disagree", self.serial_conn)

                execute_combo(self.serial_conn, "narration")
                self.update_interaction_state(response, all_states)

        return total_prompts_given, total_prompts_answered

    def collect_child_understanding(self):
        """Collects the final understanding of the child after storytelling."""
        # execute_combo(self.serial_conn, "prompt")
        # speak_text("Can you tell me what you understood about the story?")
        text = "Can you tell me what you understood about the story?"
        speak_and_execute_async(text, "motivation", self.serial_conn)
        self.state = "listening"
        execute_combo(self.serial_conn, "listening")

        silence_count = 0
        final_understanding = []
        start_time = time.time()
        max_listening_time = 120

        while time.time() - start_time < max_listening_time:
            response = listen_for_child_response(timeout=10)
            self.state = "idle"

            if not response.strip():
                silence_count += 1
                if silence_count >= 3:
                    # speak_text("I didn't hear anything, let's continue.")
                    text = "I didn't hear anything, let's continue."
                    speak_and_execute_async(text, "motivation", self.serial_conn)
                    self.state = "idle"
                    break
                else:
                    # execute_combo(self.serial_conn, "motivation")
                    # speak_text("C'mon, you can do it!")
                    text = "C'mon, you can do it!"
                    speak_and_execute_async(text, "motivation", self.serial_conn)
                    self.state = "listening"
            else:
                silence_count = 0
                words = response.split()
                if len(words) >= 3:
                    final_understanding.append(response)

        execute_combo(self.serial_conn, "narration")
        return " ".join(final_understanding)

    def perform_closure(self, storytelling_frame, all_states):
        """Handles the closure of the storytelling session."""
        closure_prompt = self.prompt_manager.get_random_prompt("Closure")
        # execute_combo(self.serial_conn, "outro")
        # speak_text(closure_prompt["text"] if closure_prompt else "Goodbye! See you next time!")
        # execute_combo(self.serial_conn, "shutdown")
        text = closure_prompt["text"] if closure_prompt else "Goodbye! See you next time!"
        speak_and_execute_async(text, "outro", self.serial_conn)
        execute_combo(self.serial_conn, "shutdown")
        self.update_engagement_state(storytelling_frame, all_states)
        storytelling_frame.end_storytelling()

    def generate_and_save_report(self, final_understanding_text, all_states, total_prompts_given, total_prompts_answered):
        """Generates the evaluation report and saves it."""
        evaluation_report = self.evaluator.evaluate(
            final_understanding_text, all_states, total_prompts_given, total_prompts_answered)

        self.update_vocabulary_from_understanding(
            final_understanding_text, self.selected_student_id, self.session_id)
        self.save_report_to_db(evaluation_report, total_prompts_answered)
        # self.print_evaluation_summary(evaluation_report)

    def update_interaction_state(self, response, all_states):
        """Updates the state based on the child's response."""
        current_state = self.state_updater.update_state_from_story(
            Mode.INTERACTION, response)
        all_states.append(current_state)  
        return current_state

    def save_report_to_db(self, evaluation_report, total_prompts_answered):
        """Saves the evaluation report to the database via an API request."""

        if not hasattr(self, 'session_id') or not self.session_id:
            print("Error: Session ID not found. Report not saved.")
            return

        # API URL
        api_url = "http://127.0.0.1:8000/api/create-student-report/"

        # Report Data
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

    def save_words_to_db(self, student_id, session_id, new_words):
        """
        Sends newly learned words to the backend API to update the student's vocabulary.
        """
        if not new_words:
            print("No new words to save.")
            return

        api_url = "http://127.0.0.1:8000/api/add-student-vocabulary/"

        data = {
            "student_id": student_id,
            "session_id": session_id,
            "words": list(new_words)
        }

        try:
            response = requests.post(api_url, json=data)
            response_data = response.json()

            if response.status_code == 201:
                print(
                    f"Words successfully saved: {response_data['added_words']}")
            else:
                print(f"Error saving words: {response_data}")

        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {str(e)}")

    def update_vocabulary_from_understanding(self, final_understanding_text, student_id, session_id):
        """
        Sends the child's retelling words to the API for processing.
        """
        words = set(final_understanding_text.split()
                    )  # Convert to set to avoid duplicates
        self.save_words_to_db(student_id, session_id, words)

    def update_storytelling_state(self, detected_state):
        """Update state in response to detected emotions, gaze, and head pose."""
        # print("Updated Storytelling State:", detected_state)
        # Here, you can use `detected_state` to update a state manager, log data, or adjust the RL system
