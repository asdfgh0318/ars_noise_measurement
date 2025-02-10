from measure import measurement
from measurement_station import ConnectionParams
import sys

ARGS = sys.argv

# Configuration start
# See README

CONN_PARAMS = ConnectionParams(
        stand_tty='/dev/ttyUSB0',
        # stand_tty='COM7',
        nor_addr='10.145.1.1',
        nor_ftp_user='AAAA',
        nor_ftp_pass='1234',
        nor_recordings_dir='/SD Card/NorMeas/Nor14530408/TEST'
        )


# PWM_RANGE = list(range(1200, 1500, 100)) + list(range(1500,1800,50))
PWM_RANGE = range(1100, 1800, 100)
# PWM_RANGE = [1100, 1200, 1300, 1350, 1375, 1400, 1425, 1450, 1475, 1500]

# OUTPUT_FILE = folder1/subfolderfolder
OUTPUT_FILE = ARGS[1]

# Configuration end

measurement(CONN_PARAMS, PWM_RANGE, OUTPUT_FILE)
