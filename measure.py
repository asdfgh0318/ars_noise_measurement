import asyncio
from measurement_station import ConnectionParams, meas_series
import pickle


def measurement(params: ConnectionParams, pwm_range, filename: str):
    x = asyncio.run(meas_series(params, pwm_range))

    with open(filename, 'wb') as f:
        pickle.dump(x, f)
