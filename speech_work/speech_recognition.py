import os
import queue
import sounddevice as sd
import vosk
import json

MODEL_PATH = "./Resources/vosk-model-small-en-us-0.15"

if not os.path.exists(MODEL_PATH):
    print("Model folder not found! Make sure you extracted it correctly.")
    exit(1)

model = vosk.Model(MODEL_PATH)

samplerate = 16000 
q = queue.Queue()


def callback(indata, frames, time, status):
    """Callback function to process audio input"""
    if status:
        print(status, flush=True)
    q.put(bytes(indata))  


with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    rec = vosk.KaldiRecognizer(model, samplerate)

    print("🎤 Speak now... (Press Ctrl+C to stop)")

    try:
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                print("You said:", result["text"])
    except KeyboardInterrupt:
        print("\n🔴 Stopping recognition.")
