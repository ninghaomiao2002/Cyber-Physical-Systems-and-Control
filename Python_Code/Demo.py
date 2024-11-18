import logging
import sys
import time
from threading import Event
import speech_recognition as sr
from pynput import keyboard
import cv2
import mediapipe as mp
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie 
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

# set the uri for the drone
URI = uri_helper.uri_from_env(default='radio://0/17/2M/EE5C21CF16')

DEFAULT_HEIGHT = 0.6
deck_attached_event = Event()

logging.basicConfig(level=logging.ERROR)
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

def detect_gesture(landmarks):
    # Extract keypoint coordinates too fingers
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    ring_tip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    index_mcp = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_mcp = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_mcp = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_mcp = landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    thumb_mcp = landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]

    def is_finger_straight(mcp, tip):
        return mcp.y > tip.y

    def is_finger_bent(mcp, tip):
        return mcp.y < tip.y

    # detection finger gesture 1
    if is_finger_straight(index_mcp, index_tip) and is_finger_bent(middle_mcp, middle_tip) \
            and is_finger_bent(ring_mcp, ring_tip) and is_finger_bent(pinky_mcp, pinky_tip):
        return "1"  # Move forward

    # detection finger gesture 2
    if is_finger_straight(index_mcp, index_tip) and is_finger_straight(middle_mcp, middle_tip) \
            and is_finger_bent(ring_mcp, ring_tip) and is_finger_bent(pinky_mcp, pinky_tip):
        return "2"  # Move backward

    # detection finger gesture 3
    if is_finger_straight(index_mcp, index_tip) and is_finger_straight(middle_mcp, middle_tip) \
            and is_finger_straight(ring_mcp, ring_tip) and is_finger_bent(pinky_mcp, pinky_tip):
        return "3"  # Move left

    # detection finger gesture 4
    if is_finger_bent(index_mcp, thumb_tip) and is_finger_straight(index_mcp, index_tip) \
            and is_finger_straight(middle_mcp, middle_tip) and is_finger_straight(ring_mcp, ring_tip) \
            and is_finger_straight(pinky_mcp, pinky_tip):
        return "4"  # Move right

    # detection finger gesture 5
    if is_finger_straight(index_mcp, thumb_tip) and is_finger_straight(middle_mcp, middle_tip) \
            and is_finger_straight(ring_mcp, ring_tip) and is_finger_straight(pinky_mcp, pinky_tip) \
            and is_finger_straight(thumb_mcp, thumb_tip):
        return "5"  # Move up

    # detection finger gesture 0
    if is_finger_bent(index_mcp, index_tip) and is_finger_bent(middle_mcp, middle_tip) \
            and is_finger_bent(ring_mcp, ring_tip) and is_finger_bent(pinky_mcp, pinky_tip):
        return "0"  # Move down

    return None  # No gesture recognized

# check if the deck is attached
def param_deck_flow(_, value_str):
    value = int(value_str)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')

# press function for different keys
def on_press(key, mc):
    try:
        if key.char == 'w': # move forward
            mc.forward(0.2, 1)
        elif key.char == 's': # move back
            mc.back(0.2, 1)
        elif key.char == 'a': # move left
            mc.left(0.2, 1)
        elif key.char == 'd': # move right
            mc.right(0.2, 1)
        elif key.char == 'q': # turn left
            mc.turn_left(15)
        elif key.char == 'e': # turn right
            mc.turn_right(15)
        elif key.char == 'r': # go up
            mc.up(0.1)
        elif key.char == 'f': # go down
            mc.down(0.1)
        elif key.char == '1': # function NO.1 draw a circle
            mc.circle_left(0.3, 0.5, 360)
    except AttributeError:
        pass

# press ESC to exit & land
def on_release(key): 
    if key == keyboard.Key.esc:
        return False

# selection for gesture, voice or keyboard control
def control_method():
    while True:  # Keep asking until a valid input is provided
        method = input("Please choose control method of the drone: (voice or keyboard or gesture): ").lower()

        # Check if the input is either 'voice' or 'keyboard'
        if method == "voice" or method == "keyboard" or method == "gesture":
            print(f'You choose {method}')
            return method
        else:
            print("Invalid input. Please enter 'voice' or 'keyboard' or 'gesture'.")

# Functions to control the drone based on voice commands
def move_forward(mc):
    print("Moving forward")
    mc.forward(0.5, 1)

def move_back(mc):
    print("Moving back")
    mc.back(0.5, 1)

def move_left(mc):
    print("Moving left")
    mc.left(0.5, 1)

def move_right(mc):
    print("Moving right")
    mc.right(0.5, 1)

def move_up(mc):
    print("Moving up")
    mc.up(0.3, 0.6)

def move_down(mc):
    print("Moving down")
    mc.down(0.3, 0.6)

def circle_left(mc):
    print("Performing left circle")
    mc.circle_left(0.2, 0.2, 360)

def take_off(mc):
    print("Taking off")
    mc.take_off()

def land(mc):
    print("Landing...")
    mc.land()

# Command mapping based on recognized voice commands
COMMANDS = {
    "forward": move_forward,
    "backward": move_back,
    "left": move_left,
    "right": move_right,
    "up": move_up,
    "down": move_down,
    "circle": circle_left,
}

def listen_for_command():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 1500
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    
    except sr.UnknownValueError:
        print("Sorry, I did not understand the command.")
        return None
    
    except sr.RequestError as e:
        print(f"Error with Google Web Speech API: {e}")
        return None

# Main function for controlling the drone based on voice commands
def drone_voice_control(scf):
    failed_attempts = 0  # Counter for failed attempts

    while True:
        command = listen_for_command()  # Listen for a command
        
        if command:
            command = command.strip().lower()  # Normalize the command
            first_letter = command[0]  # Get the first letter of the command

            print(f"Recognized command: '{command}'")  # Debugging output

            # Process command based on the full command or the first letter to improve accuracy
            if command in ["forward"] or first_letter == 'f':
                move_forward(mc)
            elif command in ["backward", "back"] or first_letter == 'b':
                move_back(mc)
            elif command in ["left", "lift", "love"] or first_letter in ['l']:
                mc.left(0.5, 1)
            elif command in ["right", "move right"] or first_letter in ['r', 'm']:
                move_right(mc)
            elif command in ["circle"] or first_letter == 'c':
                circle_left(mc)
            elif command in ["take off", "takeoff"] or first_letter == 't':
                take_off(mc)
            elif command in ["stop"] or first_letter in ['s']:
                land(mc)
                print("Stopping...")
                break
            else:
                print(f"Command not recognized: '{command}'. Try a valid command.")
                failed_attempts += 1  # Increment failed attempts
                continue  # Skip the failed attempt handling below

            # Reset failed attempts if a valid command was recognized
            failed_attempts = 0

        else:
            print("No command recognized.")
            failed_attempts += 1  # Increment if no command was understood

        # Check if there have been 5 consecutive failed attempts
        if failed_attempts >= 5:
            print("No valid commands heard after 5 tries. Landing the drone.")
            land(mc)
            break

def applying_gesture():
    last_gesture = None  # Initialize last gesture variable

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Render results and detect gestures
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS)
                gesture = detect_gesture(hand)
                print(f"Detected Gesture: {gesture}")

                # Control drone based on detected gesture
                if gesture == "1":
                    mc.start_forward(0.2)  # Move forward
                elif gesture == "2":
                    mc.start_back(0.2)  # Move backward
                elif gesture == "3":
                    mc.start_left(0.2)  # Move left
                elif gesture == "4":
                    mc.start_right(0.2)  # Move right
                elif gesture == "5":
                    mc.start_down(0.2)  # Move down
                elif gesture == "0":
                    mc.start_up(0.2)  # Move up
                elif gesture == 'None':
                    mc.stop()
                time.sleep(1)

        cv2.imshow('Hand Tracking', image)

        if cv2.waitKey(10) & 0xFF == 27:
            break

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        scf.cf.param.add_update_callback(group='deck', name='bcFlow2', cb=param_deck_flow)
        time.sleep(1)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)

        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            # Start listening for voice commands
            case = control_method()
            
            # implement voice function
            if case == "voice":
                drone_voice_control(scf)

            # implement keyboard function
            if case == "keyboard":
                with keyboard.Listener(on_press=lambda key: on_press(key, mc), on_release=on_release) as listener:
                    listener.join()

            # implement gesture function
            if case == "gesture":
                cap = cv2.VideoCapture(0)
                with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.3) as hands:
                    applying_gesture()
                cap.release()
                cv2.destroyAllWindows()