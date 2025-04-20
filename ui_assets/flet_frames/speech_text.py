import json
import queue
import threading
import time
import pyttsx3
import os
import sounddevice as sd

import vosk

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Adjust index for desired voice
engine.setProperty('rate', 200)
engine.setProperty('volume', 1.0)

speech_queue = queue.Queue()

def speech_loop():
    while True:
        text = speech_queue.get()
        if text is None:
            break
        print("Speaking:", text)
        engine.say(text)
        engine.runAndWait()
        print("Finished:", text)
        speech_queue.task_done()

speech_thread = threading.Thread(target=speech_loop, daemon=True)
speech_thread.start()

def speak_text(text):
    print("Queued:", text)
    speech_queue.put(text)

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
print(sd.query_devices(sd.default.device[0]))
stream.start()

def listen_for_child_response(timeout=60):
    """ Listen for the child's response using Vosk. """
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
        
        rec.AcceptWaveform(data)
    
    final_result = json.loads(rec.FinalResult())
    transcript += " " + final_result.get("text", "")
    transcript = transcript.strip()
    
    print(f"📝 You said: {transcript}")
    return transcript