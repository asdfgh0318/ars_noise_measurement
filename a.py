import struct
import serial
import asyncio
import time
import operator
import functools
import threading

import msp
import async_serial
from thrust_stand import ThrustStand, raw_thrust, raw_torque

# baud 250000
#version 1585
print(time.time())
s = serial.Serial(port='/dev/ttyUSB0', baudrate=250000)
print(time.time())

# ccode = bytes((1,))

# s.write(ccode)



while True:
    l = s.readline()
    print(l)
    if l == b'Ready\r\n':
        break

print('dupa')

# # s.write(make_msp(2))

# # while True:
# #     i = s.read()
# #     print(f'{i[0]}: ({i})')

pwm = 1000

# def xxx():
#     while True:
#         code, data = read_msp(s)
#         print('aaa')
#         print(code)
#         print(data.hex())
#         esc_voltage, esc_current, esc_power, load_thrust, load_left, rot_e, rot_o, temp0, temp1, temp2, basic_data_flag, acc_x, acc_y, acc_z, vibration, raw_pressure_p, raw_pressure_t, load_right, pro_data_flag = struct.unpack_from('<ffffffffffchhhhhhfc', data)
#         # print(esc_voltage)
#         # print(esc_current)
#         # print(esc_power)
#         # print(rot_e)

#         print(load_thrust)
#         print(load_left)
#         print(load_right)

#         # print(acc_x)
#         # print(acc_y)
#         # print(acc_z)

# t = threading.Thread(target=xxx)
# t.start()

# while True:
#     s.write(make_poll(pwm))
#     time.sleep(0.2)

async def main():
    r, w = async_serial.wrap_serial(s)
    m = msp.MSPSlave(r, w)
    await m.ensure_reader()
    print('aaaaa')
    thr = ThrustStand(m)
    await thr.ensure_running()
    await asyncio.sleep(10)

    sample = thr.samples[-1]
    thrust_tare = raw_thrust(sample.load_thrust)
    torque_tare = raw_torque(sample.load_left, sample.load_right)

    while True:
        # thr.mot_pwm = 2000
        # await asyncio.sleep(1000)
        thr.mot_pwm += 10
        # print(thr.mot_pwm)
        # await asyncio.sleep(1)
        await thr.stabilize_rpm(4, 1)
        sample = thr.samples[-1]
        thrust = raw_thrust(sample.load_thrust) - thrust_tare
        torque = raw_torque(sample.load_left, sample.load_right) - torque_tare
        print(f'{thr.mot_pwm} {sample.rot_e} {thrust} {torque}')

        if thr.mot_pwm >= 1900:
            break



    


    # while True:
    #     global pwm
    #     print(pwm)
    #     res = await m.do_poll(pwm)
    #     print(res.load_thrust*1000)
    #     await asyncio.sleep(0.2)
        # print(res)


# def worker():
#     asyncio.run(main())

# t = threading.Thread(target=worker)
# t.start()

asyncio.run(main())
