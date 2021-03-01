import asyncio
import logging

from veil_api_client import VeilClient

logging.basicConfig(level=logging.DEBUG)


async def simple_main():
    token = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.ey'
    server = '192.168.11.102'

    async with VeilClient(server_address=server, token=token, url_max_length=200) as session:
        domain = session.domain('67e45225-db3f-4474-b334-e8d83ef89a2a')
        # list of domain tags
        await domain.info()
        print(domain.verbose_name)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(simple_main())
