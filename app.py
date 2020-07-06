# -*- coding: utf-8 -*-
"""Temporary runner."""
import asyncio

import uvloop

from veil_api_client import DomainConfiguration, VeilClient, VeilRestPaginator, VeilClientSingleton


# TODO: tests - доработать по отчету coverage
# TODO: api_object_prefix - в README указать, что это путь к сущности на ECP
# TODO: description - документация
# TODO: logging - wknd
# TODO: retry - wknd
# TODO: типы возвращаемых значений - wknd


async def main():
    """Примеры использования."""
    token_102 = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxNjUsInVzZXJuYW1lIjoiYXBpLWNsaSIsImV4cCI6MTU5MzU5OTkyNiwic3NvIjpmYWxzZSwib3JpZ19pYXQiOjE1OTM1MTM1MjZ9.9EEhiXhxkWiOuRCscgyq6Go-O5Utofeg0j9iQzB55i8'
    server_address_115 = '192.168.11.115'
    server_address_102 = '192.168.11.102'
    factory = VeilClientSingleton()

    print(factory.instances)
    factory.add_client(server_address_102, token_102)
    print(factory.instances)
    factory.add_client(server_address_115, token_102)
    factory.add_client(server_address_102, token_102)
    print(factory.instances)
    await factory.remove_client(server_address_102)
    await factory.remove_client(server_address_115)
    print(factory.instances)


    # paginator_type = VeilRestPaginator('vdi-server')
    # paginator_type2 = VeilRestPaginator(limit=1)
    # [D 200626 15:21:20 logging:26] http://192.168.11.115/api/tasks/4c3c7065-c742-4f78-93bc-6a5689a391b3: An internal error occurred while processing request: [Errno 32] Broken pipe
    # TODO: возвращается каждый раз открытая ранее сессия?
    # async with VeilClient(server_address=server_address_102, token=token_102, session_reopen=True,
    #                       ujson_=False, timeout=5) as session:
    #     domains_list_response = await session.domain().list()
    #     # TODO: почему не подставляется status_code?
    #     print('domain status: {}'.format(domains_list_response.status_code))
    #     print('domain data: {}'.format(domains_list_response.data))
    #     print('domain header: {}'.format(domains_list_response.headers))

    # print('Session 1 is closed.')
    # # del session
    # session_obj = VeilClient(server_address=server_address_102, token=token_102, ssl_enabled=False,
    #                          extra_params={'async': 1},
    #                          timeout=2, session_reopen=False)
    #
    # domain = session_obj.domain()
    # domain_configuration = DomainConfiguration(verbose_name='cli2-tst',
    #                                            parent='9a4aa3e4-29b6-448e-b779-4380e7736e2f',
    #                                            node='6edf3154-10c3-431d-adbc-234d04301b6f',
    #                                            datapool='f7c2aa60-390d-4fe6-b4ac-015a9b73a244'
    #                                            )
    # create_response = await domain.create(domain_configuration)
    # print(create_response.status_code)
    # print(create_response.data)
    #
    # await session_obj.close()
    # print('Session 2 is closed.')
    #
    # create_response = await domain.create(domain_configuration)
    # print(create_response.status_code)
    # print(create_response.data)
    #
    # await session_obj.close()
    # print('Session 3 is closed.')


uvloop.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
