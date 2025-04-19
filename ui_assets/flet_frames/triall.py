# import threading
# import queue
# import time
# import pyttsx3

# speech_queue = queue.Queue()

# def speech_loop():
#     # Initialize engine inside the thread.
#     engine = pyttsx3.init()
#     while True:
#         text = speech_queue.get()
#         if text is None:
#             break
#         print("Speaking:", text)
#         engine.say(text)
#         engine.runAndWait()  # Blocks until the current text is spoken.
#         print("Finished speaking:", text)
#         speech_queue.task_done()

# # Start the speech loop in a separate thread.
# speech_thread = threading.Thread(target=speech_loop, daemon=True)
# speech_thread.start()

# def speak_text(text):
#     """Add the text to the queue for speech."""
#     print("Queued:", text)
#     speech_queue.put(text)

# # Test the queue and speaking behavior.
# speak_text("Hello! How are you today?")
# speak_text("I'm Tello, your talking friend!")
# speak_text("Let's have some fun with speech synthesis.")
# speak_text("This is a test of the speech queue.")
# speak_text("Prashidika Tiwari!")

# # Wait until all speech tasks in the queue are finished.
# speech_queue.join()  # This will block until the queue is empty.

# print(f"Queue size after speaking: {speech_queue.qsize()}")


# import threading
# import pyttsx3

# # Global lock to ensure only one speech call runs at a time.
# _speech_lock = threading.Lock()
# # Single shared pyttsx3 engine instance.
# _engine = pyttsx3.init()

# def speak_text_sync(text):
#     """
#     Synchronously speaks the provided text.
#     This call will block until the text is fully spoken.
#     """
#     with _speech_lock:
#         print("Speaking:", text)
#         _engine.say(text)
#         _engine.runAndWait()  # This call blocks until the utterance is complete.
#         print("Finished speaking:", text)

# # Example usage of the function:
# if __name__ == "__main__":
#     speak_text_sync("Hello! How are you today?")
#     speak_text_sync("I'm Tello, your talking friend!")
#     speak_text_sync("Let's have some fun with speech synthesis.")
#     speak_text_sync("This is a test of the synchronous speech function.")
#     speak_text_sync("Prashidika Tiwari!")


import subprocess
import sys
import os
import threading

# Global lock to ensure only one speech is processed at a time.
_speak_lock = threading.Lock()

def speak_text(text):
    with _speak_lock:
        # Determine the absolute path to the TTS worker script.
        worker_script = os.path.join(os.path.dirname(__file__), "tts_worker.py")
        # Run the worker script synchronously so that the function waits until the speech is complete.
        subprocess.run([sys.executable, worker_script, text])
