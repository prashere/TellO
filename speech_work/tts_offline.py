import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty('voices')

engine.setProperty('voice', voices[0].id) 

engine.setProperty('rate', 200)  
engine.setProperty('volume', 1.0)  

text = "The dog is barking."

engine.say(text)
engine.runAndWait()
print("Text-to-speech successfully executed.")
