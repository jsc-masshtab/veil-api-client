# -*- coding: utf-8 -*-
"""Temporary runner."""
import asyncio
# import uvloop
import logging

from veil_api_client import VeilClient, VeilClientSingleton, VeilCacheOptions, VeilDomain, VeilRetryOptions, VeilRestPaginator

logging.basicConfig(level=logging.DEBUG)

token = 'jwt eyJ0eXAiOiJKV1DYFeGNGySnmeI'
server = '192.168.14.151'


async def simple_main():
    async with VeilClient(server_address=server, token=token) as session:
        # Настраиваем пагинатор - сортировка по полю verbose_name, первые 10 записей.
        paginator = VeilRestPaginator(ordering='verbose_name', limit=10)
        # У каждой сессии есть атрибут - сущность на ECP VeiL.
        veil_domain_entity = session.domain()
        # получаем ответ со списком вм
        veil_response = await veil_domain_entity.list(paginator=paginator)

        # Ответ списком имеет 200й статус, ответ на результат задачи скорее всего будет в 202 статусе
        if veil_response.status_code == 418:
            raise AssertionError('VeiL ECP проходит процедуру обновления. Попробуйте позже.')
        elif not veil_response.success:
            raise AssertionError('Ошибка получения информации от VeiL.')

        # Включаем каждую из полученных ВМ
        for domain in veil_response.response:
            start_response = await domain.start()
            if not start_response.success:
                raise AssertionError(start_response.error_detail)


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
