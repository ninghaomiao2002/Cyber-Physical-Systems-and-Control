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

URI = uri_helper.uri_from_env(default='radio://0/17/2M/EE5C21CF16')

DEFAULT_HEIGHT = 0.6
BOX_LIMIT = 0.5
deck_attached_event = Event()

logging.basicConfig(level=logging.ERROR)


def param_deck_flow(_, value_str):
    value = int(value_str)
    print(value)
    if value:
        deck_attached_event.set()
        print('Deck is attached!')
    else:
        print('Deck is NOT attached!')


def move_around(scf):
    time.sleep(1)
    mc.forward(0.5, 1)
    time.sleep(1)
    mc.back(1, 1)
    time.sleep(1)
    mc.forward(0.5, 1)
    time.sleep(1)
    mc.left(0.5, 1)
    time.sleep(1)
    mc.right(1, 1)
    time.sleep(1)
    mc.left(0.5, 1)
    time.sleep(1)
    mc.up(0.3, 0.6)
    time.sleep(1)
    mc.down(0.3, 0.6)


def left_circle(scf):
    time.sleep(1)
    mc.circle_left(0.5, 0.5, 360)
    time.sleep(1)


if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        scf.cf.param.add_update_callback(group='deck', name='bcFlow2',
                                         cb=param_deck_flow)
        time.sleep(1)

        if not deck_attached_event.wait(timeout=5):
            print('No flow deck detected!')
            sys.exit(1)

        with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
            move_around(scf)
            left_circle(scf)
