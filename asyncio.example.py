import asyncio
import aiohttp
import async_timeout


async def main():
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(10):
            async with session.get('http://python.org') as response:
                html = await response.text()
                print(html)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())