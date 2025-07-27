import cv2
import math
import time
import pyttsx3
import speech_recognition as sr
import busio
import threading
from ultralytics import YOLO
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
from rapidfuzz import process

# Initialise systems
tts = pyttsx3.init()
listener = sr.Recognizer()
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50  # Standard frequency for servos

# Define servo channels
base = pca.channels[1]  # 360 degree servo
#5 LFD-06 Servos (180 degrees)
shoulder = pca.channels[2]
elbow = pca.channels[3]
wrist = pca.channels[4]
wrist_rotation = pca.channels[5]
grip = pca.channels[6]  # Between 90 & 180 degrees

# Load YOLO model
model = YOLO("best_ncnn_model")

# Object classes
classNames = ['Blue-Cube', 'Blue-Cylinder', 'Blue-Hexagonal-Prism', 'Blue-Triangular-Prism',
              'Green-Cube', 'Green-Cylinder', 'Green-Hexagonal-Prism', 'Green-Triangular-Prism',
              'Red-Cube', 'Red-Cylinder', 'Red-Hexagonal-Prism', 'Red-Triangular-Prism',
              'White-Cube', 'White-Cylinder', 'White-Hexagonal-Prism', 'White-Triangular-Prism']
classColours = [(255, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 255, 0), (0, 255, 0), (0, 255, 0), (0, 255, 0),
                (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 255), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]

# Servo movement functions
def set_servo_angle(channel, angle):
    min_pulse, max_pulse = 500, 2500  # based on the servo's datasheet 500/0.5ms is the min position & 2500/2.5ms is the max position
    if channel == base:
        angle = max(0, min(angle, 360))  # Constrain base servo between 0 and 360
        pulse = int(min_pulse + (angle / 360.0) * (max_pulse - min_pulse))
    else:
        angle = max(0, min(angle, 180))  # Constrain other servos between 0 and 180
        pulse = int(min_pulse + (angle / 180.0) * (max_pulse - min_pulse))
    duty_cycle = int(pulse / 20000 * 65535)
    channel.duty_cycle = duty_cycle


# Predefined arm positions
def start_position():
    set_servo_angle(base, 270)
    time.sleep(1)
    set_servo_angle(shoulder, 130)
    time.sleep(1)
    set_servo_angle(elbow, 10)
    time.sleep(1)
    set_servo_angle(wrist, 140)
    time.sleep(1)
    set_servo_angle(wrist_rotation, 90)
    time.sleep(1)
    print("Moved to start position")


def bowl1():
    set_servo_angle(base, 270)
    time.sleep(1)
    set_servo_angle(shoulder, 130)
    time.sleep(1)
    set_servo_angle(elbow, 0)
    time.sleep(1)
    set_servo_angle(wrist, 140)
    time.sleep(1)
    set_servo_angle(wrist_rotation, 90)
    time.sleep(1)
    print("Moved to bowl 1")


def bowl2():
    set_servo_angle(base, 230)
    time.sleep(1)
    set_servo_angle(shoulder, 130)
    time.sleep(1)
    set_servo_angle(elbow, 0)
    time.sleep(1)
    set_servo_angle(wrist, 140)
    time.sleep(1)
    set_servo_angle(wrist_rotation, 90)
    time.sleep(1)
    print("Moved to bowl 2")


def bowl3():
    set_servo_angle(base, 270)
    time.sleep(1)
    set_servo_angle(shoulder, 120)
    time.sleep(1)
    set_servo_angle(elbow, 0)
    time.sleep(1)
    set_servo_angle(wrist, 180)
    time.sleep(1)
    set_servo_angle(wrist_rotation, 90)
    time.sleep(1)
    print("Moved to bowl 3")


def bowl4():
    set_servo_angle(base, 230)
    time.sleep(1)
    set_servo_angle(shoulder, 120)
    time.sleep(1)
    set_servo_angle(elbow, 0)
    time.sleep(1)
    set_servo_angle(wrist, 180)
    time.sleep(1)
    set_servo_angle(wrist_rotation, 90)
    time.sleep(1)
    print("Moved to bowl 4")

def speak(text):
    tts.say(text)  # Queues text to be spoken
    tts.runAndWait()  # Process and output the text in queue


def recognise_speech():
    with sr.Microphone() as mic:
        listener.adjust_for_ambient_noise(mic)  # Adjust the mic for ambient noise
        try:
            audio = listener.listen(mic)  # Record audio from the mic
            command = listener.recognize_google(audio)  # STT(speech-to-text) using Google or Sphinx speech recognition API
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

# Sorting function
def detect_and_sort(mode):
    sorting = False
    while not sorting:
        success, img = cap.read()
        results = model(img)
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = math.ceil((box.conf[0] * 100)) / 100
                if confidence > 0.8:
                    cls = int(box.cls[0])
                    detected_object = classNames[cls]
                    print(f" Class =, {detected_object}, Confidence {confidence}")
                    colour = classColours[cls]
                    org = [x1, y2]
                    cv2.putText(img, classNames[cls], org, cv2.FONT_HERSHEY_SIMPLEX, 1, colour, 2)
                    cv2.rectangle(img, (x1, y1), (x2, y2), colour, 3)

                    sorting = True
                    start_position()
                    time.sleep(1)
                    if mode == "colour":
                        print("sorting by colour")
                        speak("sorting by colour")
                        if 'Blue' in detected_object:
                            bowl1()
                        if 'Green' in detected_object:
                            bowl2()
                        if 'Red' in detected_object:
                            bowl3()
                        if 'White' in detected_object:
                            bowl4()
                        else:
                            print("there is nothing to sort")
                            speak("there is nothing to sort")
                            sorting = False
                            time.sleep(5)
                            
                    if mode == "shape":
                        print("sorting by shape")
                        speak("sorting by shape")
                        if 'Cube' in detected_object:
                            bowl1()
                        if 'Cylinder' in detected_object:
                            bowl2()
                        if 'Hexagonal-Prism' in detected_object:
                            bowl3()
                        if 'Triangular-Prism' in detected_object:
                            bowl4()
                        else:
                            print("there is nothing to sort")
                            speak("there is nothing to sort")
                            time.sleep(5)
                            sorting = False
                    break
        cv2.imshow('Shape and Colour Detection', img)
        if cv2.waitKey(1) == ord('q'):
            break


cap = cv2.VideoCapture(0)
# Set Image resolution to 640x640
cap.set(3, 640)
cap.set(4, 640)  
start_position()

def main():
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
                detect_and_sort("colour")
            if action == "Sorting by shape":
                detect_and_sort("shape")
        else:
            speak("command not recognised")
            print("command not recognised")
            
                    
main()
cap.release()
cv2.destroyAllWindows()
pca.deinit()   
#threading.Thread(target=main).start()
#threading.Thread(target=detect_and_sort).start()
