import asyncio
from collections.abc import Callable, Iterable, Sequence
from typing import Optional
from urllib import parse
import aioftp
import websockets
from websockets.asyncio.client import ClientConnection

from logger import spr
import norsonic_fetcher

MSG_OUT_NEW = "NewMeasurement"
MSG_OUT_START = "StartMeasurement"

KEY_STATE = 'State'
KEY_FILENAME = 'GraphHeader'
VAL_STATE_NEW = ''
VAL_STATE_RECORDING = "<span title='Running' class='icon-play4 greenFg'></span>"
VAL_STATE_WAITING = "<span title='Waiting' class='icon-busy'></span>"
VAL_STATE_DONE = "<span title='Saved' class='icon-disk'></span>"

def parse_msg(msg: str) -> dict[str, str]:
    ret = {}
    for l in msg.splitlines():
        # print(f'par "{l}"')
        if len(l) == 0:
            continue
        if l == 'clear':
            break
        if ':' not in l:
            print(f'W: Unexpected line in message: {l}')
            continue

        k, v = l.split(':', 1)
        if k in ret:
            if ret[k] == v:
                continue
            if len(v) == 0:
                continue
            print(f'W: Duplicate key detected ({k}: {v})')
            raise RuntimeError()
        ret[k] = v

    return ret
    
class NSWSConnection:
    # def __init__(self, ws: Web)
    ...


async def recv_msg(sock: ClientConnection) -> dict[str, str]:
    recv = await sock.recv()
    if not isinstance(recv, str):
        raise RuntimeError('Invalid message received')
    msg = parse_msg(recv)
    return msg


async def wait_for_state(sock: ClientConnection, state: str, expected_states: Iterable[str] = []) -> dict[str, str]:
    while True:
        msg = await recv_msg(sock)
        # spr(msg)
        if KEY_STATE in msg:
            if msg[KEY_STATE] == state:
                return msg
            elif msg[KEY_STATE] not in expected_states:
                spr(f'W: Unexpected state received: {msg[KEY_STATE]}')


async def record(sock: ClientConnection, start_callback: Optional[Callable[[], None]] = None):
    await sock.send(MSG_OUT_NEW)
    spr('Initializing measurement')
    await wait_for_state(sock, VAL_STATE_NEW, (VAL_STATE_DONE, ))

    await sock.send(MSG_OUT_START)
    spr('Starting measurement')
    await wait_for_state(sock, VAL_STATE_WAITING, (VAL_STATE_NEW, ))
    spr('Waiting for start')
    await wait_for_state(sock, VAL_STATE_RECORDING)

    if start_callback is not None:
        start_callback()

    spr('Waiting for finish')
    msg = await wait_for_state(sock, VAL_STATE_DONE)
    return msg[KEY_FILENAME]

async def open_connection(address: str) -> ClientConnection:
    return await websockets.connect(f'ws://{address}/live', ping_interval=None)


# async def main():
#     sock = await websockets.connect('ws://10.145.1.1/live')
#     spr('Connected to server')
#     name = await record(sock)
#     spr(f'finished {name}')
#     c = aioftp.Client(parse_list_line_custom=norsonic_fetcher.ftp_parse_line)
#     res = await c.connect('10.145.1.1')
#     res = await c.login('AAAA', '1234')
#     global x
#     # x = norsonic_fetcher.parse_report(await norsonic_fetcher.ftp_fetch(c, norsonic_fetcher.recording_path(name)))
#     x = norsonic_fetcher.parse_report(await norsonic_fetcher.ftp_fetch(c, norsonic_fetcher.FNAME))
#     print(x)


