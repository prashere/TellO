import sys
import pyttsx3

def main():
    if len(sys.argv) < 2:
        sys.exit("No text provided for TTS.")
    text = sys.argv[1]

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 200)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

if __name__ == '__main__':
    main()
