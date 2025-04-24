import asyncio
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from logging import debug
import logging
from typing import Optional

from fft import FFTData
from logger import spr
from norsonic_parser import parse_report
import thrust_stand
import norsonic

from norsonic_fetcher import nor_get_reports
from thrust_stand import ThrustStand, ThrustStandMeasurement

@dataclass(frozen=True)
class OpPointData:
    data_thrust_stand: Sequence[ThrustStandMeasurement]
    raw_nor_report: Optional[bytes]
    pwm_setpoint: int

    @property
    def nor_report_parsed(self):
        if self.raw_nor_report is None:
            raise ValueError()
        return parse_report(self.raw_nor_report)

    @property 
    def data_accustic(self):
        return self.nor_report_parsed.profile

    @property
    def data_thrust_stand_avg(self) -> ThrustStandMeasurement:
        return sum(self.data_thrust_stand, ThrustStandMeasurement.zero())/len(self.data_thrust_stand)

    @property
    def data_accustic_avg(self) -> dict[str, float]:
        return {k: sum(map(float, (row[k] for row in self.data_accustic)))/len(self.data_accustic) for k in self.data_accustic[0].keys() if k != 'Date'}

    @property
    def data_fft(self) -> FFTData:
        return FFTData(self.nor_report_parsed.glob_fft)



# import sys
# async def ainput(string: str) -> str:
#     await asyncio.get_event_loop().run_in_executor(
#             None, lambda s=string: sys.stdout.write(s+' '))
#     return await asyncio.get_event_loop().run_in_executor(
#             None, sys.stdin.readline)


@dataclass
class ConnectionParams:
    stand_tty: str
    nor_addr: str
    nor_ftp_user: str
    nor_ftp_pass: str
    nor_recordings_dir: str

async def meas_series(params: ConnectionParams, pwms: Iterable[int]):
    stand = await ThrustStand.open_connection(params.stand_tty)
    nor = await norsonic.open_connection(params.nor_addr)

    results_stand = {}
    files_nor = {}

    # TODO TARA
    sample,  = stand.get_samples_raw(1)
    stand.tare_thrust = thrust_stand.raw_thrust(sample.load_thrust)
    stand.tare_torque = thrust_stand.raw_torque(sample.load_left, sample.load_right)
    stand.tare_current = sample.esc_current

    stand.mot_pwm = 1000

    ####
    # stand.mot_pwm = 1200
    # await ainput("Press Enter to continue...")

    
    for pwm in pwms:
        stand.mot_pwm = pwm
        spr(f'Output: {pwm}PWM')
        await stand.stabilize_rpm(10, 4)
        spr(f'Starting measurement')
        stand_series_pending = stand.start_meas_series()
        #
        files_nor[pwm] = await norsonic.record(nor)
        # await asyncio.sleep(8)
        spr(f'Done')
        results_stand[pwm] =  stand.finish_meas_series(stand_series_pending)
        print(results_stand[pwm][0])

    while stand.mot_pwm > 1000:
        stand.mot_pwm -= 10
        await asyncio.sleep(0.1)

    stand.mot_pwm = 1000

    await asyncio.sleep(3)

    spr('Downlaoding reports')


    nor_reports = await nor_get_reports(params.nor_addr, params.nor_ftp_user, params.nor_ftp_pass, [files_nor[pwm] for pwm in pwms])
    spr('Done')

    ret = {
            pwm: OpPointData(
                data_thrust_stand=results_stand[pwm],
                # raw_nor_report=None
                raw_nor_report=nor_reports[i]
                ) for i, pwm in enumerate(pwms)
            }
    return ret

