import pyttsx3 # text to speech library
import speech_recognition as sr
from rapidfuzz import process  # library that uses fuzzy logic to match commands

tts = pyttsx3.init()  # Initialise text-to-speech engine
listener = sr.Recognizer()  # Initialise audio listener

def speak(text):
    tts.say(text)  # Queues text to be spoken
    tts.runAndWait()  # Process and output the text in queue


def recognise_speech():
    with sr.Microphone() as mic:
        listener.adjust_for_ambient_noise(mic)  # Adjust the mic for ambient noise
        try:
            audio = listener.listen(mic)  # Record audio from the mic
            command = listener.recognize_google(audio)  # STT(speech-to-text) using Google or sphinx speech recognition API
            print(f"Command heard: {command}")
            return command
        except sr.UnknownValueError:  # Occurs when speech is not heard or understood
            print("Sorry, I didn't catch that.")
            speak("Sorry, I didn't catch that, please try again.")
            return None
        except sr.RequestError:  # Occurs when the laptop or pc is offline
            print("Speech recognition service is unavailable.")
            return None


def match_commands(user_input):  # Function to Match the command to predefined actions
    commands = {
        "sort them by colour": "sorting by colour",
        "organise them by colour": "sorting by colour",
        "sort them by shape": "sorting by shape",
        "organise them by shape": "sorting by shape"
        }  # command input : Action

    # Use RapidFuzz to find the closest match
    if user_input:  # If there is user input attempt to match it.
        best_match = process.extractOne(user_input, commands.keys())
        if best_match and best_match[1] > 80:  # Confidence threshold
            action = commands[best_match[0]]
            return best_match[0], action
    return None, None


speak("System ready. Say sort by colour or sort by shape.")
print("System ready. Say sort by colour or sort by shape.")

while True:
    user_input = recognise_speech()
    if user_input is None:
        continue
    matched_command, action = match_commands(user_input)
    if matched_command:  
        print(f"The Command recognised is: {matched_command} and the action is {action}")
        speak(action)
        if action == "Sorting by colour":
            print(action)
        if action == "Sorting by shape":
            print(action)
    else:
        speak("command not recognised")
        print("command not recognised")
