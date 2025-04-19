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
