# -*- coding: utf-8 -*-
"""Temporary runner."""
import asyncio

import uvloop

from veil_api_client.https_client import VeilClient


async def main():
    # TODO: использовать новые токены на Veil
    token_102 = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNTkyOTI0NjIyLCJzc28iOmZhbHNlLCJvcmlnX2lhdCI6MTU5MjgzODIyMn0.tLFtZWFZ5ifFwvbVLf7NTlaHQUEalRuiF8xa39-bTgs'
    server_address_102 = '192.168.11.102'

    async with VeilClient(server_address=server_address_102, token=token_102, ssl_enabled=False,
                          extra_headers={'Accept-Language': 'ru'},
                          extra_params={'async': 1},
                          timeout=10) as session:

        # domain = session.domain('dffc20c3-620d-40f3-9366-f48f0eb65882')
        # task = session.task('60398dbd-732e-4a45-a6ce-c86c35abb22f')
        vdisk = session.vdisk('1548fd13-02c6-4490-8387-d8a27077c7d7')
        # task_list_response = await task.list()
        # print(task_list_response.data)
        # task_info_response = await task.info()
        # print(task_info_response.data)
        print('-----')
        print(vdisk.public_attrs)
        await vdisk.info()
        print(vdisk.shareable)
        print(vdisk.domain)
        print(vdisk.verbose_name)
        print(vdisk.status)
        print(vdisk.api_object_id)
        print(vdisk.uuid_)
        print(vdisk.size)

uvloop.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
