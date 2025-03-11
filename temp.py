import json
import time
import os
import cv2
import queue
import pyttsx3
import sounddevice as sd
import vosk

# Import your custom classes
from rl_framework.state import State, Mode, EngagementLevel, EmotionalState, ResponseQuality, PromptNecessity, ResponseLength, VocabularyUsage
from story_handler.story import Story
from story_handler.prompt import PromptManager

# -----------------------------------
# Initialize Text-to-Speech (TTS)
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Adjust index for desired voice
engine.setProperty('rate', 200)
engine.setProperty('volume', 1.0)

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# -----------------------------------
# Initialize Speech-to-Text (STT) using Vosk
MODEL_PATH = "speech_work/Resources/vosk-model-small-en-us-0.15"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model folder not found: {MODEL_PATH}")
model = vosk.Model(MODEL_PATH)
samplerate = 16000
q = queue.Queue()

def stt_callback(indata, frames, time_info, status):
    if status:
        print(status, flush=True)
    q.put(bytes(indata))

stream = sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                           channels=1, callback=stt_callback)
stream.start()

def listen_for_child_response(timeout=60):
    """
    Listen for the child's response using Vosk for the full timeout period.
    :param timeout: Time in seconds to continuously listen.
    :return: The full transcribed text from the child's speech.
    """
    # Clear any existing data in the queue
    while not q.empty():
        q.get()
    
    rec = vosk.KaldiRecognizer(model, samplerate)
    start_time = time.time()
    transcript = ""

    print("\n🎤 Speak now... (Listening for", timeout, "seconds)")

    while time.time() - start_time < timeout:
        try:
            data = q.get(timeout=0.5)
        except queue.Empty:
            continue
        
        # Feed the data to the recognizer
        rec.AcceptWaveform(data)
        # Append partial result if available (optional: can also use PartialResult() for debugging)
        # We don't break early; we just accumulate the text from final results.
    
    # After timeout, get any final pending result
    final_result = json.loads(rec.FinalResult())
    transcript += " " + final_result.get("text", "")
    transcript = transcript.strip()
    
    print(f"📝 You said: {transcript}")
    return transcript



# -----------------------------------
# Load Story and Prompts
story_file = 'dataset/story_corpus/stories/easy/story3.json'  # Adjust path as needed
with open(story_file, "r", encoding="utf-8") as f:
    story_data = json.load(f)
story = Story(story_data)

prompt_file = 'dataset/prompts.json'  # Adjust path as needed
with open(prompt_file, "r", encoding="utf-8") as f:
    prompt_data = json.load(f)
prompt_manager = PromptManager(prompt_data)

# -----------------------------------
# Main Storytelling Flow
def run_storytelling():
    # 1. Greeting
    greeting_prompt = prompt_manager.get_random_prompt("Greeting")
    greeting_text = greeting_prompt["text"] if greeting_prompt else "Hello, welcome to TellO!"
    speak_text(greeting_text)
    time.sleep(1)

    # 2. Inform about the story
    speak_text("Now I will tell you a story.")
    time.sleep(1)

    # 3. Start the story
    sentence = story.start_story()
    sentence_count = 0

    while sentence:
        sentence_count += 1

        # Display the image associated with the current sentence, if available
        image_file = story.get_current_image()  # Returns the image filename
        if image_file:
            image_file = "dataset/story_corpus/img/" + image_file
            img = cv2.imread(image_file)
            if img is not None:
                cv2.imshow("Current Image", img)
                # Ask: "What do you see?" and wait for 30 seconds
                speak_text("What do you see?")
                child_image_response = listen_for_child_response(timeout=2)
                print("Child's image response:", child_image_response)
                speak_text("Nice work.")
                # Close image window after 30 seconds
                cv2.waitKey(1)  # Ensure the window displays properly
                cv2.destroyWindow("Current Image")
            else:
                print(f"Image {image_file} could not be loaded.")
        else:
            print("No image associated with this sentence.")

        # Speak the sentence text
        speak_text(sentence["Text"])
        time.sleep(1)

        # After every even-numbered sentence, prompt the child for an interaction
        if sentence_count % 2 == 0:
            interaction_prompt = sentence.get("InteractionPrompt", "What do you think?")
            speak_text(interaction_prompt)
            child_response = listen_for_child_response(timeout=2)
            print("Child's interaction response:", child_response)
            speak_text("Alright, that's good.")
            time.sleep(1)

        # Get the next sentence
        sentence = story.get_next_sentence()

    # End with a closure prompt
    closure_prompt = prompt_manager.get_random_prompt("Closure")
    closure_text = closure_prompt["text"] if closure_prompt else "Goodbye! See you next time!"
    speak_text(closure_text)

# -----------------------------------
# Main Execution
if __name__ == "__main__":
    try:
        run_storytelling()
    except Exception as e:
        print("An error occurred:", e)
    finally:
        stream.stop()
        stream.close()
        cv2.destroyAllWindows()
