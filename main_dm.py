import asyncio
from measurement_station import ConnectionParams, meas_series


CONN_PARAMS = ConnectionParams(
        stand_tty='/dev/ttyUSB0',
        nor_addr='10.145.1.1',
        nor_ftp_user='AAAA',
        nor_ftp_pass='1234',
        nor_recordings_dir='/SD Card/NorMeas/Nor14530408/TEST'
        )



range(1200, 1500, 50)


async def main():
    global x
    x = await meas_series(CONN_PARAMS, range(1200, 1800, 100))



# logging.basicConfig(level=logging.INFO)
asyncio.run(main(), debug=True)

import pickle
import sys

with open(sys.argv[1], 'wb') as f:
    pickle.dump(x, f)
