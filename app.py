# -*- coding: utf-8 -*-
"""Temporary runner."""
import asyncio
import uvloop

from veil_api_client import VeilClientSingleton, VeilRestPaginator, VeilClient, VeilCacheOptions, DomainConfiguration

# TODO: tests - доработать по отчету coverage
# TODO: api_object_prefix - в README указать, что это путь к сущности на ECP
# TODO: description - документация
# TODO: retry
# TODO: описать как подключить собственный кеш на примере redis?


async def main():
    """Примеры использования."""
    token1 = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxNjUsInVzZXJuYW1lIjoiYXBpLWNsaSIsImV4cCI6MTkwODI2MjI1Niwic3NvIjpmYWxzZSwib3JpZ19pYXQiOjE1OTM3NjYyNTZ9._41CVXezP1vDHoZyQ71UcadqPdti7-tmy_teEjfBgio'
    server1 = '192.168.11.115'
    cache_options = VeilCacheOptions(ttl=10, cache_type='memcached', server=('localhost', 11211))
    async with VeilClient(server1, token1, cache_opts=None) as veil_single:
        # domains_list_response = await veil_single.domain('06bb682f-672a-40ef-aff8-cb43dfe9d4f2').info()
        # if domains_list_response.success:
        #     print('request is successfull')
        #     print('response_data_object:', domains_list_response.response[0])
        #     print('response_data_object_template:', domains_list_response.response[0].template)
        #     print('response_data_dict:', domains_list_response.value)
        #     print('response_data_list:', domains_list_response.paginator_results)
        # else:
        #     print('request has error')
        #
        # clusters_list_response = await veil_single.cluster().list()
        # if clusters_list_response.success:
        #     print('request is successfull')
        #     for cluster in clusters_list_response.response:
        #         print('response_data_object name:', cluster.verbose_name)
        #     print('response_data_dict:', clusters_list_response.value)
        #     print('response_data_list:', clusters_list_response.paginator_results)
        # else:
        #     print('request has error')
        #
        # domain = veil_single.domain()
        # domain_configuration = DomainConfiguration(verbose_name='',
        #                                            parent='9a4aa3e4-29b6-448e-b779-4380e7736e2f',
        #                                            node='6edf3154-10c3-431d-adbc-234d04301b6f',
        #                                            datapool='f7c2aa60-390d-4fe6-b4ac-015a9b73a244'
        #                                            )
        #
        # create_response = await domain.create(domain_configuration)
        # print('create response:', create_response)
        # print(create_response.success)
        # print(create_response.response)
        # print(create_response.value)
        # # TODO: добавить на VDI обработку неправильного кода, сейчас {'errors': [{'domain': "The domain doesn't exist with the id 9a4aa3e4-29b6-448e-b779-4380e7736e2f", 'code': 'invalid'}]}
        # print(create_response.data)
        domain_client = veil_single.domain()
        multi_remove_response = await domain_client.multi_remove(entity_ids=["b3498951-290b-4430-84e7-28c2f4dd315b"])
        print(multi_remove_response)
        # print(create_response.status_code)
        # print(create_response.data)

        # for domain in domains_list.response:
        #     print(domain.status)
        # print('-----------')
        # for domain in domains_list.paginator_results:
        #     print(domain.get('id'))
        # for domain in domains_list.paginator_results:
        #     print(domain)
        # domains_list = await veil_single.domain().list()
        # print('domains list:', domains_list.data)
        # for domain in domains_list.paginator_results:
        #     print('domain:', domain)
        #     print('parent:', domain.get('parent'))
        # print('domains list:', domains_list.data)
        # domains_list = await veil_single.domain('6d45f973-402e-4936-9c7e-195bcba94351').info()
        # print('domains list:', domains_list.data)
        # domains_list = await veil_single.domain('6d45f973-402e-4936-9c7e-195bcba94331').info()
        # print('domains list:', domains_list.data)

    # Инициализируем класс для работы с клиентами
    # veil_client = VeilClientSingleton(cache_opts=cache_options)
    # Добавляем подключение к первому контроллеру
    # session1 = veil_client.add_client(server1, token1)
    # domains_list_response = await session1.domain().list()
    # Добавляем еще одно подключение к контроллеру
    # В результате у session2 будет ссылка на тот же клиент, что передан для session
    # session2 = veil_client.add_client(server1, token1)
    # Устанавливаем соединение с еще одним контроллером
    # session2 = veil_client.add_client(server2, token2)
    # domains_list_response2 = await session2.domain().list()
    # Удаляем существующую сессию для контроллера, давая возможность изменить ему настройки
    # await veil_client.remove_client(server1)
    # ...
    # Перед завершением приложения закрываем все используемые сессии
    # instances = veil_client.instances
    # for instance in instances:
    #     await instances[instance].close()
    # async with VeilClient(server_address=server_address_102, token=token_102, session_reopen=True,
    #                       ujson_=False, timeout=5) as session:
    #     domains_list_response = await session.domain().list()
    #     print('domain status: {}'.format(domains_list_response.status_code))
    #     print('domain data: {}'.format(domains_list_response.data))
    #     print('domain header: {}'.format(domains_list_response.headers))

    # print('Session 1 is closed.')
    # del session
    # session_obj = VeilClient(server_address=server_address_115, token=token_115, ssl_enabled=False,
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
    # #
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
