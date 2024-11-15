import logging
import sys
import time
from threading import Event
import speech_recognition as sr
from pynput import keyboard
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

URI = uri_helper.uri_from_env(default='radio://0/17/2M/EE5C21CF16')

DEFAULT_HEIGHT = 0.6
deck_attached_event = Event()

logging.basicConfig(level=logging.ERROR)


def param_deck_flow(_, value_str):
    value = int(value_str)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')


def on_press(key, mc):
    try:
        if key.char == 'w':
            mc.forward(0.2, 1)
        elif key.char == 's':
            mc.back(0.2, 1)
        elif key.char == 'a':
            mc.left(0.2, 1)
        elif key.char == 'd':
            mc.right(0.2, 1)
        elif key.char == 'q':
            mc.turn_left(15)
        elif key.char == 'e':
            mc.turn_right(15)
        elif key.char == 'r':  # go up
            mc.up(0.1)
        elif key.char == 'f':  # do down
            mc.down(0.1)
        elif key.char == '1':  # function NO.1 draw a circle
            mc.circle_left(0.3, 0.5, 360)
    except AttributeError:
        pass


def on_release(key):  # press ESC to exit & land
    if key == keyboard.Key.esc:
        return False


def control_method():
    while True:  # Keep asking until a valid input is provided
        method = input("Please choose control method of the drone: (voice or keyboard): ").lower()

        # Check if the input is either 'voice' or 'keyboard'
        if method == "voice" or method == "keyboard":
            print(f'You choose {method}')
            return method
        else:
            print("Invalid input. Please enter 'voice' or 'keyboard'.")


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
    mc.circle_left(0.5, 0.5, 360)


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


def listen_for_commands(mc):
    recognizer = sr.Recognizer()

    while True:
        try:
            # Capture voice input from the microphone
            with sr.Microphone() as source:
                print("Listening for command...")
                audio = recognizer.listen(source)

            # Recognize speech using Google's API
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)

            # Execute the corresponding drone function
            for command, action in COMMANDS.items():
                if command in text:
                    action(mc)  # Execute the corresponding movement
                    break
            else:
                print("Command not recognized. Please say again.")

        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except KeyboardInterrupt:
            print("Exiting voice control")
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
            if case == "voice":
                listen_for_commands(mc)
            if case == "keyboard":
                with keyboard.Listener(on_press=lambda key: on_press(key, mc), on_release=on_release) as listener:
                    listener.join()