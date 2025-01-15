import pickle
import math

from measurement_station import OpPointData

class MyCustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == '__main__':
            module = 'measurement_station'
        return super().find_class(module, name)

f = open('m3.pickle', 'rb')
data = MyCustomUnpickler(f).load()
d1 = data[1100]

def prrow(r: OpPointData):
    print(r.data_thrust_stand_avg.thrust, end=',')
    print(r.data_thrust_stand_avg.torque, end=',')
    print(r.data_thrust_stand_avg.rot_speed, end=',')
    for v in r.data_accustic_avg.values():
        print(v, end=',')
    print()

print(list(list(data.values())[0].data_accustic_avg.keys()))

for pwm, d in data.items():
    prrow(d)

# thrusts = [d.data_thrust_stand_avg.thrust for d in data.values()]
# powers = [d.data_thrust_stand_avg.torque * d.data_thrust_stand_avg.rot_speed * -2*math.pi / 7 for d in data.values()]
# laeqs = [d.data_accustic_avg['S1 LAeq'] for d in data.values()]
# lzeqs = [d.data_accustic_avg['S1 LZeq'] for d in data.values()]

# import matplotlib.pyplot as plt

# _, ax1 = plt.subplots()

# ax1.plot(thrusts, laeqs, label="LAeq [dB]", color='blue')
# ax1.plot(thrusts, lzeqs, label="LZeq [dB]", color='red')

# ax1.set_xlabel("Thrust [N]")

# ax2 = ax1.twinx()
# ax2.plot(thrusts, powers, label="Power [W]", color='green')

# ax1.legend()
# ax2.legend(loc=1)

# plt.title("Powertrain noise measurement")

# plt.savefig('fig.svg')
