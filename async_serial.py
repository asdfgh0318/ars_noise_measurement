import asyncio
from typing import cast
from serial.serialutil import SerialException
from typing_extensions import Buffer
import serial

class X(asyncio.StreamReaderProtocol):
    ...

class SerialTransport(asyncio.Transport):
    ser: serial.Serial
    loop: asyncio.BaseEventLoop

    def __init__(self, loop, protocol, serial: serial.Serial):
        serial.timeout = 0

        self.loop = loop
        self.protocol = protocol
        self.ser = serial

        self.paused = False
        self._read_ready()

    def write(self, data: Buffer):
        self.ser.write(data)

    def _read_ready(self):
        READ_BUFF_SIZE = 2048

        while True:
            try:
                data = self.ser.read(READ_BUFF_SIZE)
            except SerialException as e:
                self.protocol.connection_lost(e)
                return
            if len(data) == 0:
                break
            self.protocol.data_received(data)

        if self.ser.fd is None:
            raise RuntimeError('Invalid serial fd')
        self.loop.add_reader(cast(int, self.ser.fd), self._read_ready)

    def is_closing(self) -> bool:
        print('asked if closing')
        return True


# def serial_create_connection(protocol_factory, serial):
#     loop = asyncio.get_event_loop()
#     protocol = protocol_factory()
#     transport = SerialTransport(loop, protocol, serial)
#     return transport, protocol


# def serial_open_connection(serial):
#     reader = streams.StreamReader()
#     protocol = streams.StreamReaderProtocol(reader)
#     factory = lambda: protocol
#     transport, _ = serial_create_connection(factory, serial)
#     writer = streams.StreamWriter(transport, protocol, reader, asyncio.get_running_loop())
#     return reader, writer

def wrap_serial(serial: serial.Serial):
    loop = asyncio.get_running_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    transport = SerialTransport(loop, protocol, serial)
    writer = asyncio.StreamWriter(transport, protocol, reader, loop)
    return reader, writer
