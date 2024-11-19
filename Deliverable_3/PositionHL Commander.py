# GNU General Public License

"""
This script shows the basic use of the PositionHlCommander class.

Simple example that connects to the crazyflie at `URI` and runs a
sequence. This script requires a deck with an absolute positioning system.

The PositionHlCommander uses position setpoints.

Change the URI variable to your Crazyflie configuration.
"""
import cflib.crtp
import time
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/17/2M/EE5C21CF16')

def simple_sequence():
    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        with PositionHlCommander(scf, controller=PositionHlCommander.CONTROLLER_PID) as pc:
            for _ in range(1):
                time.sleep(0.5)
                pc.go_to(0.0, 0.0, 0.2)
                time.sleep(0.5)
                pc.go_to(0.2, 0.2, 0.2)
                time.sleep(0.5)
                pc.go_to(0.0, 0.0, 0.2)
                time.sleep(0.5)
                pc.go_to(0.0, 0.0, 0.1)
                time.sleep(0.5)


if __name__ == '__main__':
    cflib.crtp.init_drivers()

    simple_sequence()