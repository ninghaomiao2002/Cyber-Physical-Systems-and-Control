import logging
import sys
import time
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper

import speech_recognition as sr

# Set up URI for drone connection
URI = uri_helper.uri_from_env(default='radio://0/17/2M/EE5C21CF16')
DEFAULT_HEIGHT = 0.5
deck_attached_event = Event()

logging.basicConfig(level=logging.ERROR)

# Callback function for detecting the deck
def param_deck_flow(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')

# Functions to control the drone movements
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

def circle_left(mc):
    print("Circling left")
    mc.circle_left(0.5, 0.5, 360)

def take_off(mc):
    print("Taking off")
    mc.take_off()

def land(mc):
    print("Landing...")
    mc.land()


# Function to recognize voice commands
def listen_for_command():
    recognizer = sr.Recognizer()
    # Tune the energy threshold for better speech detection
    recognizer.energy_threshold = 1500  # You can adjust this value based on your environment
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
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        failed_attempts = 0  # Counter for failed attempts

        while True:
            command = listen_for_command()  # Listen for a command
            if command:
                command = command.strip().lower()  # Normalize the command
                first_letter = command[0]  # Get the first letter of the command

                print(f"Recognized command: '{command}'")  # Debugging output

                # Process command based on the full command or the first letter
                if command in ["forward"] or first_letter == 'f':
                    move_forward(mc)
                elif command in ["backward", "back"] or first_letter == 'b':
                    move_back(mc)
                elif command in ["left", "lift", "move left","love"] or first_letter in ['l', 'm']:
                    move_left(mc)
                elif command in ["right", "write"] or first_letter == 'r':
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
                print("No command recognized.")  # Debugging output
                failed_attempts += 1  # Increment if no command was understood

            # Check if there have been 3 consecutive failed attempts
            if failed_attempts >= 3:
                print("No valid commands heard after 3 tries. Landing the drone.")
                land(mc)
                break


if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # Set up the deck detection
        scf.cf.param.add_update_callback(group='deck', name='bcFlow2', cb=param_deck_flow)
        time.sleep(1)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)

        # Control the drone via voice commands based on words or first letters
        drone_voice_control(scf)


    


