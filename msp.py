from asyncio import Future, StreamReader, StreamWriter, Task, shield
import asyncio
import functools
import operator
import struct
from typing import Awaitable, Dict, Optional, Self
from dataclasses import dataclass

MSP_MAGIC_OUT = b"$R<"
MSP_MAGIC_IN = b"$R>"
MSP_CODE_POLL = 3

def make_msp(code: int, data: bytes = b'') -> bytes:
    ret = bytearray(MSP_MAGIC_OUT)
    if len(data) > 255:
        raise ValueError()
    ret.append(len(data))
    ret.append(code)
    ret += data
    checksum = functools.reduce(operator.xor, map(int, ret[len(MSP_MAGIC_OUT):]))
    ret.append(checksum)
    return bytes(ret)

async def read_msp(r: StreamReader) -> tuple[int, bytes]:
    magic_pos = 0
    while magic_pos < len(MSP_MAGIC_IN):
        b, = await r.readexactly(1)
        if b == MSP_MAGIC_IN[magic_pos]:
            magic_pos += 1
        else:
            magic_pos = 0
            print('Unexpected byte from RCBenchmark serial')
    size, = await r.readexactly(1)
    code, = await r.readexactly(1)
    data = await r.readexactly(size)
    checksum, = await r.readexactly(1)
    _ = checksum
    return code, data


def make_poll(esc_pwm: int) -> bytes: 
    data = struct.pack('<HHHH', esc_pwm, 0, 0, 0)
    # data = struct.pack('>HHHH', esc_pwm, 0, 0, 0)
    # return make_msp(MSP_CODE_POLL, data)
    return data


#        esc_voltage, esc_current, esc_power, load_thrust, load_left, rot_e, rot_o, temp0, temp1, temp2, basic_data_flag, acc_x, acc_y, acc_z, vibration, raw_pressure_p, raw_pressure_t, load_right, pro_data_flag = struct.unpack_from('<ffffffffffchhhhhhfc', data)

@dataclass
class PollResponse:
    esc_voltage: float
    esc_current: float
    esc_power: float
    load_thrust: float
    load_left: float
    rot_e: float
    rot_o: float
    temp0: float
    temp1: float
    temp2: float
    basic_data_flag: int
    acc_x: int
    acc_y: int
    acc_z: int
    vibration: int
    raw_pressure_p: int
    raw_pressure_t: int
    load_right: float
    pro_data_flag: int

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        unpacked = struct.unpack_from('<ffffffffffchhhhhhfc', data)
        # print(unpacked)
        return cls(*unpacked)




class MSPSlave:
    w: StreamWriter
    r: StreamReader

    pending_requests: Dict[int, Future[bytes]]
    _reader_task: Optional[Task]


    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.r = reader
        self.w = writer
        self._reader_task = None
        self.pending_requests = {}

    async def ensure_reader(self):
        if self._reader_task is None:
            self._reader_task = asyncio.create_task(self._reader())

    async def _reader(self):
        try:
            while True:
                code, data = await read_msp(self.r)
                self.handle_packet(code, data)
        except Exception as e:
            for req in self.pending_requests.values():
                req.set_exception(e)
            

    def handle_packet(self, code: int, data: bytes):
        if code in self.pending_requests:
            self.pending_requests[code].set_result(data)
        else:
            raise RuntimeError(f'Unexpected packet: {code}')

    def do_request(self, code: int, data: bytes) -> Awaitable[bytes]: 
        if code in self.pending_requests:
            raise RuntimeError('Duplicate request')
        f = Future()
        def future_done(_):
            del self.pending_requests[code]
        self.pending_requests[code] = f
        f.add_done_callback(future_done)
        self.w.write(make_msp(code, data))
        return shield(f)

    async def do_poll(self, esc_pwm: int) -> PollResponse:
        resp = await self.do_request(MSP_CODE_POLL, make_poll(esc_pwm))
        return PollResponse.from_bytes(resp)
