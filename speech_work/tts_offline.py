import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty('voices')

engine.setProperty('voice', voices[0].id) 

engine.setProperty('rate', 200)  
engine.setProperty('volume', 1.0)  

text = "Hello! This is a different voice. Today is Sunday and the weather is nice."

engine.say(text)
engine.runAndWait()
