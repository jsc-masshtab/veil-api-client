# -*- coding: utf-8 -*-
"""Temporary runner."""
import asyncio
import uvloop
import logging

from veil_api_client import VeilClient, VeilRetryConfiguration

logging.basicConfig(level=logging.DEBUG)

token = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6ImRldnlhdGtpbl92ZGkiLCJleHAiOjE5MjY2Nzk4OTUsInNzbyI6ZmFsc2UsIm9yaWdfaWF0IjoxNjEyMTgzODk1fQ.UKf7Sr4JB6tQw8Ftn5Cex0ZO6Qg4uNG24827fohWVXM'
server = '192.168.11.102'

manual_retry = VeilRetryConfiguration(num_of_attempts=10)


async def simple_main():
    async with VeilClient(server_address=server, token=token) as session:
        # domain = session.domain(retry_opts=manual_retry)
        domain = session.domain('e4b2179e-8539-47b2-965e-4c706c0b3129')
        # list of domains
        list_response = await domain.tags_list()
        for domain in list_response.response:
            print('domain:', domain)


uvloop.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(simple_main())
