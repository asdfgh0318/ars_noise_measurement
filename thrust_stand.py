import asyncio
import numbers
import statistics
from asyncio.futures import Future
from asyncio.tasks import Task
from collections.abc import Sequence
from dataclasses import dataclass, fields
import operator
from time import time
from typing import Any, Callable, Optional, Self, cast
from msp import MSPSlave, PollResponse


HIST_SIZE = 100
GRAVITY_CONST = 9.80665
HINGE_DISTANCE = 0.07492
THRUST_CONST = 1000 * 5 / 5 * GRAVITY_CONST
TORQUE_CONST = 1000 * 2 / 5 * GRAVITY_CONST * HINGE_DISTANCE / 2

CAL_POLES = 14
CAL_HINGE_LEFT = 1.2100092475098374
CAL_HINGE_RIGHT = 1.2590952216896254
CAL_LEFT = 0.9663293361785854
CAL_RIGHT = -0.9575068323376389
CAL_THRUST = -0.9516456828857573
CAL_TORQUE_LEFT = CAL_LEFT * CAL_HINGE_LEFT
CAL_TORQUE_RIGHT = CAL_RIGHT * CAL_HINGE_RIGHT
CAL_SYNCSPEED = 2/CAL_POLES * 2* 3.1415

def raw_torque(val_left: float, val_right: float) -> float:
    return ((val_right * CAL_TORQUE_RIGHT) - (val_left * CAL_TORQUE_LEFT)) * TORQUE_CONST

def raw_thrust(val: float) -> float:
    return val * CAL_THRUST * THRUST_CONST

def raw_torque_resp(raw: PollResponse) -> float:
    return raw_torque(raw.load_left, raw.load_right)

def raw_thrust_resp(raw: PollResponse) -> float:
    return raw_thrust(raw.load_thrust)

@dataclass
class PendingMeasurementSeries:
    start_sample_num: int
    

@dataclass
class ThrustStandMeasurement:
    thrust: float
    torque: float
    rot_speed: float
    volt: float
    current: float

    @classmethod
    def num_operation(cls, op: Callable[[numbers.Real, numbers.Real], numbers.Real], a: Self, b: Self | numbers.Real):
        results = {}
        for f in fields(cls):
            val_a: numbers.Real = a if isinstance(a, numbers.Real) else getattr(a, f.name) 
            val_b: numbers.Real = b if isinstance(b, numbers.Real) else getattr(b, f.name) 
            results[f.name] = op(val_a, val_b)
        return cls(**results)
    
    def __add__(self, other: Self):
        return self.num_operation(operator.add, self, other)

    def __truediv__(self, divisor):
    # def __truediv__(self, divisor):
        return self.num_operation(operator.truediv, self, divisor)

    def __pow__(self, power):
        return self.num_operation(operator.pow, self, power)

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0, 0, 0, 0)


class ThrustStand:
    mot_pwm: int
    msp: MSPSlave
    sample_number: int
    samples_raw: list[PollResponse]

    tare_thrust: float
    tare_torque: float
    tare_current: float
    

    _next_sample_future: Future
    _poller_task: Optional[Task]
    _closed: bool

    def __init__(self, msp: MSPSlave):
        self.msp = msp
        self.mot_pwm = 1000
        self._poller_task = None
        self.sample_number = 0
        self.samples_raw = []
        self._next_sample_future = Future()


    async def _poller(self):
        while True:

            await asyncio.gather(
                    asyncio.sleep(0.03),
                    self._do_poll()
                    )

    async def _do_poll(self):

        res = await self.msp.do_poll(self.mot_pwm)
        self.samples_raw.append(res)
        self.sample_number += 1
        # print(res.rot_e)
        self._next_sample_future.set_result(None)
        self._next_sample_future = Future()

    async def ensure_running(self):
        if self._poller_task is None:
            self._poller_task = asyncio.create_task(self._poller())

    async def wait_samples(self, n):
        for _ in range(n):
            await self.next_sample()

    async def stabilize_rpm(self, window: int, tolerance: float):
        await self.wait_samples(window)

        while True:
            samples = self.samples_raw[-window:]
            rpms = list(map(lambda s: s.rot_e, samples))

            if max(rpms) - min(rpms) < tolerance:
                return
            # print(rpms)
            await self.next_sample()

    def next_sample(self) -> Future:
        return asyncio.shield(self._next_sample_future)
    
    def sample_from_raw(self, raw: PollResponse) -> ThrustStandMeasurement:
        return ThrustStandMeasurement(
                raw_thrust_resp(raw) - self.tare_thrust,
                raw_torque_resp(raw) - self.tare_torque, raw.rot_e,
                raw.esc_voltage,
                raw.esc_current - self.tare_current,
            )

    def get_samples_raw(self, n: int) -> Sequence[PollResponse]:
        return self.samples_raw[-n:]

    def get_samples(self, n: int) -> Sequence[ThrustStandMeasurement]:
        return list(map(self.sample_from_raw, self.get_samples_raw(n)))

    def start_meas_series(self) -> PendingMeasurementSeries:
        return PendingMeasurementSeries(self.sample_number)

    def finish_meas_series(self, meas: PendingMeasurementSeries) -> Sequence[ThrustStandMeasurement]:
        return self.get_samples(self.sample_number - meas.start_sample_num)

    @staticmethod
    async def open_connection(tty: str):
        thr = ThrustStand(await MSPSlave.open_connection(tty))
        await thr.ensure_running()
        await asyncio.sleep(5)
        return thr


