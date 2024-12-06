import asyncio
from asyncio.futures import Future
from asyncio.tasks import Task
from time import time
from typing import Optional, cast
from msp import MSPSlave, PollResponse


HIST_SIZE = 100
GRAVITY_CONST = 9.80665
HINGE_DISTANCE = 0.07492
THRUST_CONST = 1000 * 5 / 5 * GRAVITY_CONST
TORQUE_CONST = 1000 * 2 / 5 * GRAVITY_CONST * HINGE_DISTANCE / 2

CAL_HINGE_LEFT = 1.2100092475098374
CAL_HINGE_RIGHT = 1.2590952216896254
CAL_LEFT = 0.9663293361785854
CAL_RIGHT = -0.9575068323376389
CAL_THRUST = 0.9516456828857573
CAL_TORQUE_LEFT = CAL_LEFT * CAL_HINGE_LEFT
CAL_TORQUE_RIGHT = CAL_RIGHT * CAL_HINGE_RIGHT

def raw_torque(val_left: float, val_right: float) -> float:
    return ((val_right * CAL_TORQUE_RIGHT) - (val_left * CAL_TORQUE_LEFT)) * TORQUE_CONST

def raw_thrust(val: float) -> float:
    return val * CAL_THRUST * THRUST_CONST

class ThrustStandMeasurement:
    pass


class ThrustStand:
    mot_pwm: int
    msp: MSPSlave
    sample_number: int
    samples: list[PollResponse]

    tare_thrust: float
    tare_torque: float
    

    _next_sample_future: Future
    _poller_task: Optional[Task]
    _closed: bool

    def __init__(self, msp: MSPSlave):
        self.msp = msp
        self.mot_pwm = 1000
        self._poller_task = None
        self.samples = []
        self._next_sample_future = Future()


    async def _poller(self):
        while True:

            await asyncio.gather(
                    asyncio.sleep(0.03),
                    self._do_poll()
                    )

    async def _do_poll(self):

        res = await self.msp.do_poll(self.mot_pwm)
        self.samples.append(res)
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
            samples = self.samples[-window:]
            rpms = list(map(lambda s: s.rot_e, samples))

            if max(rpms) - min(rpms) < tolerance:
                return
            await self.next_sample()




    def next_sample(self) -> Future:
        return asyncio.shield(self._next_sample_future)

