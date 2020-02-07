import asyncio
from async_timeout import timeout
import time


async def http_client(host, port, msg, loop):

    reader, writer = await asyncio.open_connection(
        host, port, loop=loop
    )
    writer.write(msg.encode())
    data = await reader.read()
    print(f'Received: {data.decode()}')
    writer.close()
    #await asyncio.sleep(30)



async def check_specify_time():

    host = '169.254.12.61'
    port = 8010
    msg = (
        f'GET /server/check_specify_condition_table HTTP/1.1\r\n'
        'Host: localhost:8010\r\n'
        '\r\n'
        '\r\n'
    )
    loop = asyncio.get_event_loop()
    #loop.run_until_complete(http_client(host, port, msg, loop))
    print('サーバへ時間条件の確認をリクエスト')
    task = asyncio.create_task(http_client(host, port, msg, loop))
    await task
    loop.close()


async def main():
    #while(True)
    await check_specify_time()

asyncio.run(main())
