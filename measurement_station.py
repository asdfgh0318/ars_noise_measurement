import asyncio
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from logging import debug
import logging

from logger import spr
import thrust_stand
import norsonic

from norsonic_fetcher import nor_get_reports, recording_path
from thrust_stand import ThrustStand, ThrustStandMeasurement

@dataclass
class OpPointData:
    data_thrust_stand: Sequence[ThrustStandMeasurement]
    data_accustic: dict

    @property
    def data_thrust_stand_avg(self):
        return sum(self.data_thrust_stand, ThrustStandMeasurement.zero())/len(self.data_thrust_stand)

    @property
    def data_accustic_avg(self):
        return {k: sum(map(float, (row[k] for row in self.data_accustic)))/len(self.data_accustic) for k in self.data_accustic[0].keys() if k != 'Date'}



@dataclass
class ConnectionParams:
    stand_tty: str
    nor_addr: str
    nor_ftp_user: str
    nor_ftp_pass: str
    nor_recordings_dir: str

CONN_PARAMS = ConnectionParams(
        stand_tty='/dev/ttyUSB0',
        nor_addr='10.145.1.1',
        nor_ftp_user='AAAA',
        nor_ftp_pass='1234',
        nor_recordings_dir='/SD Card/NorMeas/Nor14530408/TEST'
        )

async def meas_series(params: ConnectionParams, pwms: Iterable[int]):
    stand = await ThrustStand.open_connection(params.stand_tty)
    nor = await norsonic.open_connection(params.nor_addr)

    results_stand = {}
    files_nor = {}

    # TODO TARA
    sample,  = stand.get_samples_raw(1)
    stand.tare_thrust = thrust_stand.raw_thrust(sample.load_thrust)
    stand.tare_torque = thrust_stand.raw_torque(sample.load_left, sample.load_right)
    
    for pwm in pwms:
        stand.mot_pwm = pwm
        spr(f'Output: {pwm}PWM')
        await stand.stabilize_rpm(5, 1)
        spr(f'Starting measurement')
        stand_series_pending = stand.start_meas_series()
        files_nor[pwm] = await norsonic.record(nor)
        spr(f'Done')
        results_stand[pwm] =  stand.finish_meas_series(stand_series_pending)

    stand.mot_pwm = 1000

    await asyncio.sleep(3)

    spr('Downlaoding reports')


    nor_reports = await nor_get_reports(params.nor_addr, params.nor_ftp_user, params.nor_ftp_pass, [files_nor[pwm] for pwm in pwms])
    spr('Done')

    ret = {
            pwm: OpPointData(
                data_thrust_stand=results_stand[pwm],
                data_accustic=nor_reports[i]
                ) for i, pwm in enumerate(pwms)
            }
    return ret


async def main():
    global x
    x = await meas_series(CONN_PARAMS, range(1100, 1950, 30))

# logging.basicConfig(level=logging.INFO)
# asyncio.run(main(), debug=True)
