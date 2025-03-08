import pyttsx3

engine = pyttsx3.init()

# Get available voices
voices = engine.getProperty('voices')

# Select a voice (change index as needed)
engine.setProperty('voice', voices[0].id)  # Change 1 to 0 for the default voice

# Set speech rate (optional)
engine.setProperty('rate', 200)  # Adjust speed (default ~200)
engine.setProperty('volume', 1.0)  # Adjust volume (0.0 to 1.0)

# Text to convert to speech
text = "Hello! This is a different voice. Today is Sunday and the weather is nice."

# Speak the text
engine.say(text)
engine.runAndWait()
