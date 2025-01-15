import serial
import asyncio
import time

import msp
import async_serial
from thrust_stand import ThrustStand, raw_thrust, raw_torque

# baud 250000
#version 1585
print(time.time())
s = serial.Serial(port='/dev/ttyUSB0', baudrate=250000)
print(time.time())

while True:
    l = s.readline()
    print(l)
    if l == b'Ready\r\n':
        break

print('dupa')


async def main():
    r, w = async_serial.wrap_serial(s)
    m = msp.MSPSlave(r, w)
    await m.ensure_reader()
    print('aaaaa')
    thr = ThrustStand(m)
    await thr.ensure_running()
    await asyncio.sleep(10)

    sample = thr.samples_raw[-1]
    thrust_tare = raw_thrust(sample.load_thrust)
    torque_tare = raw_torque(sample.load_left, sample.load_right)

    while True:
        if thr.mot_pwm == 1000:
            thr.mot_pwm = 1100
        thr.mot_pwm += 10
        await thr.stabilize_rpm(5, 2)
        sample = thr.samples_raw[-1]
        thrust = raw_thrust(sample.load_thrust) - thrust_tare
        torque = raw_torque(sample.load_left, sample.load_right) - torque_tare
        print(f'{thr.mot_pwm} {sample.rot_e} {thrust} {torque}')

        if thr.mot_pwm >= 1900:
            break

asyncio.run(main())
