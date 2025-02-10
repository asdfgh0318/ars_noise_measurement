import asyncio
from pathlib import Path
from re import split
from typing import Iterable, Sequence
import aioftp

from logger import spr

FNAME = '/SD Card/NorMeas/Nor14530408/TEST/VIP 124 2024-12-10 15-31-19/VIP 124 2024-12-10 15-31-19.txt'
DNAME = '/SD Card/NorMeas/Nor14530408/TEST/VIP 124 2024-12-10 15-31-19/'
RECORDINGS_PATH = '/SD Card/NorMeas/Nor14530408/TEST'
CRLF = '\r\n'
STR_DIR = '<DIR>'

def recording_path(rec_name: str) -> str:
    return f'{RECORDINGS_PATH}/{rec_name}/{rec_name}.txt'

def ftp_parse_line(line: bytes):
    l = line.decode()
    date, time, size, name = l.split(None, 3)
    _ = date
    _ = time
    attrdict = {'modify': None, 'size': 0, 'type': 'dir'}
    if size != STR_DIR:
        attrdict['type'] = 'file'
        attrdict['size'] = int(size)

    if not name.endswith(CRLF):
        raise ValueError()
    name = name[:-2]
    path = Path(name)
    return path, attrdict

async def ftp_fetch(client: aioftp.Client, path: str) -> bytes:
    spr(f'fetching {path}')
    stream = await client.download_stream(path)
    file = b''.join([block async for block in stream.iter_by_block()])
    await stream.finish()
    stream.close()
    # await asyncio.sleep(1)
    return file

async def nor_get_reports(addr: str, user: str, password: str, recs: Iterable[str]) -> Sequence[bytes]:
    pass
    # async with aioftp.Client.context(addr, user=user, password=password, parse_list_line_custom=ftp_parse_line) as ftp:
    #     return [await ftp_fetch(ftp, recording_path(p)) for p in recs]

    recs_left = list(recs)
    ret = []
    while recs_left:
        spr('Connecting to norsonic FTP...')
        try:
            async with aioftp.Client.context(addr, user=user, password=password, parse_list_line_custom=ftp_parse_line) as ftp:
                while recs_left:
                    rec = recs_left[0]
                    report = await ftp_fetch(ftp, recording_path(rec))
                    del recs_left[0]
                    ret.append(report)

        except ConnectionResetError:
            spr('Connection reset!')
            await asyncio.sleep(2)
    return ret





async def main():
    c = aioftp.Client(parse_list_line_custom=ftp_parse_line)
    res = await c.connect('10.145.1.1')
    res = await c.login('AAAA', '1234')
    global x
    ns = [
            'VIP 197 2024-12-13 11-48-21',
            'VIP 198 2024-12-13 11-48-28',
            'VIP 199 2024-12-13 11-48-35',
    ]

    x = await nor_get_reports('10.145.1.1', 'AAAA', '1234', ns)
    print(x)


    # for n in ns:
    #     x = parse_report(await ftp_fetch(c, n))
    #     print(x)

# asyncio.run(main())
