# -*- coding: utf-8 -*-
"""Temporary runner."""
import asyncio
# import uvloop
import logging

from veil_api_client import VeilClient, VeilClientSingleton, VeilCacheOptions, VeilDomain, VeilRetryOptions, VeilRestPaginator, DomainConfiguration

logging.basicConfig(level=logging.DEBUG)

token = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo0LCJ1c2VybmFtZSI6ImRldnlhdGtpbiIsImV4cCI6MTkyMjYxNzgzOCwic3NvIjpmYWxzZSwib3JpZ19pYXQiOjE2MDgxMjE4Mzh9.eGQrwaT0wXzSfBiThT00l6PGZWZvmFLnp9Eu9j48W6A'
server = '192.168.11.102'


async def simple_main():
    async with VeilClient(server_address=server, token=token) as session:
        # Список пулов ресурсов
        # veil_resource_pool = session.resource_pool()
        # veil_response = await veil_resource_pool.list()
        # for pool in veil_response.response:
        #     for arg, value in pool.public_attrs.items():
        #         if value:
        #             print('{}[{}]: {}'.format(pool.verbose_name, arg, value))
        #
        # Информация о конкретном пуле ресурсов
        # veil_resource_pool = session.resource_pool('9aa09ceb-f709-4b48-ab8a-14a8a4dba2b7')
        # veil_response = await veil_resource_pool.info()
        # for arg, value in veil_response.response[0].public_attrs.items():
        #     if value:
        #         print('[{}]: {}'.format(arg, value))
        #
        # Фильтр ВМ (без шаблонов) по пулу ресурсов
        # veil_response = await session.domain(resource_pool='9aa09ceb-f709-4b48-ab8a-14a8a4dba2b7', template=False).list(
        #     fields=['id',
        #             'verbose_name',
        #             'guest_utils'])
        # for domain in veil_response.response:
        #     print('domain {}'.format(domain.verbose_name))
        # Создане ВМ
        # Создание в старом формате
        # old_domain = DomainConfiguration(verbose_name='old_domain-2', node='36f5877a-68e9-4bb3-92df-ac3cdb4c7fd1',
        #                                  datapool='ce289d42-a13b-4ac8-b0a4-89e03b493fab',
        #                                  parent='7f250778-ce57-4dba-a411-87d88c326cf5', thin=True)
        # veil_response = await session.domain().create(domain_configuration=old_domain)
        # print(veil_response.data)

        # Создание в новом формате
        new_domain = DomainConfiguration(verbose_name='new_domain-2',
                                         resource_pool='9aa09ceb-f709-4b48-ab8a-14a8a4dba2b7',
                                         parent='7f250778-ce57-4dba-a411-87d88c326cf5', thin=True)
        veil_response = await session.domain().create(domain_configuration=new_domain)
        print(veil_response.data)

# async def extra_main():
#
#     class VmNotFoundError(AssertionError):
#         pass
#
#     class YobaVeilClient(VeilClient):
#         """Отвечает за сетевое взаимодействие с ECP VeiL."""
#
#         async def get(self, api_object, url, extra_params):
#             """Переопределен для перехвата окончательного статуса ответов."""
#             response = await super().get(api_object=api_object, url=url, extra_params=extra_params)
#             if hasattr(response, 'status_code') and hasattr(api_object, 'api_object_id') and api_object.api_object_id:
#                 if response.status_code == 404 and isinstance(api_object, VeilDomain):
#                     raise VmNotFoundError('Vm not found!')
#             return response
#
#     class YobaVeilClientSingleton(VeilClientSingleton):
#         """Хранит ранее инициализированные подключения."""
#
#         __client_instances = dict()
#
#         def __init__(self, retry_opts=None) -> None:
#             """Please see help(VeilClientSingleton) for more info."""
#             self.__TIMEOUT = 10
#             self.__CACHE_OPTS = VeilCacheOptions(ttl=10, cache_type='memcached',
#                                                  server='127.0.0.1')
#             self.__RETRY_OPTS = retry_opts
#
#         def add_client(self, server_address: str, token: str, retry_opts=None) -> 'VeilClient':
#             """Преконфигурированное подключение."""
#             if server_address not in self.__client_instances:
#                 instance = YobaVeilClient(server_address=server_address, token=token,
#                                           session_reopen=True, timeout=self.__TIMEOUT, ujson_=True,
#                                           cache_opts=self.__CACHE_OPTS,
#                                           retry_opts=self.__RETRY_OPTS)
#                 self.__client_instances[server_address] = instance
#             return self.__client_instances[server_address]
#
#         @property
#         def instances(self) -> dict:
#             """Show all instances of VeilClient."""
#             return self.__client_instances
#
#     # При проверке статуса проверяется именно тот статус, который пришел в ответе. Предположим мы хотим повторы для всех
#     # вм, что не удалось найти
#     veil_client = YobaVeilClientSingleton(
#         VeilRetryOptions(status_codes={404}, timeout_increase_step=5, num_of_attempts=3))
#
#     # Добавляем подключение к первому контроллеру
#     session1 = veil_client.add_client(server, token)
#
#     # Получаем информацию о конкретной ВМ
#     veil_domain = session1.domain('998131cc-9516-44cc-9718-55c8ea14cde6')
#     await veil_domain.info()
#
#     # Берем ответы из кеша
#     await veil_domain.info()
#     await veil_domain.info()
#     await veil_domain.info()
#     await veil_domain.info()
#
#     # Добавляем еще одно подключение к контроллеру
#     # В результате у session2 будет ссылка на тот же клиент, что передан для session
#     session2 = veil_client.add_client(server, token)
#
#     # Перед завершением приложения закрываем все используемые сессии
#     instances = veil_client.instances
#     for inst in instances:
#         await instances[inst].close()

# uvloop.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(simple_main())
