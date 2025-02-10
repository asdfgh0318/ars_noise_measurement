import asyncio

async def c1(r: asyncio.StreamReader):
    data = await r.readexactly(1)
    print(data)
    print('1')

async def c2(r: asyncio.StreamReader):
    while True:
        data = await r.readexactly(1)
        print('2')
        print(data)


async def main():
    r, w = await asyncio.open_connection('localhost', 9999)
    t1 = asyncio.create_task(c1(r))
    t2 = asyncio.create_task(c2(r))
    while True:
        await asyncio.sleep(100000)

asyncio.run(main())
