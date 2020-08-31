# -*- coding: utf-8 -*-
"""Temporary runner."""
import asyncio
import uvloop
from enum import IntEnum

from veil_api_client import VeilClientSingleton, VeilRestPaginator, VeilClient, VeilCacheOptions, DomainConfiguration, VeilGuestAgentCmd

# TODO: побороть кривые импорты
# TODO: tests - доработать по отчету coverage
# TODO: api_object_prefix - в README указать, что это путь к сущности на ECP
# TODO: description - документация
# TODO: retry
# TODO: описать как подключить собственный кеш на примере redis?


class VmPowerState(IntEnum):
    """Veil domain power states."""

    UNDEFINED = 0
    OFF = 1
    SUSPENDED = 2
    ON = 3


async def main():
    """Примеры использования."""
    token1 = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMzUsInVzZXJuYW1lIjoiZGV2eWF0a2luIiwiZXhwIjoxOTEyNzcwMTYzLCJzc28iOmZhbHNlLCJvcmlnX2lhdCI6MTU5ODI3NDE2M30.YQAWEy7Ip0XedU1e4rC9Ijv8O8LUYUlhRJ3T3vhZdRI'
    server1 = '192.168.11.115'
    rdp = True
    # cache_options = VeilCacheOptions(ttl=10, cache_type='memcached', server=('localhost', 11211))
    async with VeilClient(server1, token1, cache_opts=None) as veil_single:
        domain_client = veil_single.domain('eee8dc66-7139-4cd2-8df5-966be5bfaab0')
        # Получаем состояние параметров ВМ
        domain_response = await domain_client.info()
        print('domain response:', domain_response)
        print('domain response status:', domain_response.status_code)
        # Получаем сущность ВМ из ответа
        domain_entity = domain_response.response[0]

        # print('remote access = ', domain_entity.remote_access)
        # # Проверяем настройки удаленного доступа
        # if not domain_entity.remote_access:
        #     action_response = await domain_client.enable_remote_access()
        #     action_task = action_response.task
        #     task_completed = False
        #     while not task_completed:
        #         print('Задача еще не выполнена. Ждем 5 сек.')
        #         await asyncio.sleep(5)
        #         task_completed = await action_task.completed
        #     print('Зачада выполнена.')
        #     print('Обновляем параметры ВМ')
        #     await domain_entity.info()
        #
        # # Проверяем включена ли ВМ
        # print('Domain power state:', domain_entity.power_state)
        # if not domain_entity.power_state == VmPowerState.ON:
        #     print('ВМ выключена - нужно ее включить.')
        #     action_response = await domain_entity.start()
        #     action_task = action_response.task
        #     task_completed = False
        #     while not task_completed:
        #         print('Задача включения ВМ еще не выполнена. Ждем 3 сек.')
        #         await asyncio.sleep(3)
        #         task_completed = await action_task.completed
        #     print('Зачада выполнена.')
        #     print('Обновляем параметры ВМ')
        #     await domain_entity.info()
        #
        # # Ожидаем доступности гостевого агента.
        # while not domain_entity.guest_agent.qemu_state:
        #     await asyncio.sleep(5)
        #     await domain_entity.info()
        #     print('Гостевой агент недоступен. Ждем еще.')
        #
        # # Для подключения по rdp ВМ нужен как минимум 1 ip-адрес
        # while rdp or not domain_entity.guest_agent.first_ipv4_ip:
        #     await asyncio.sleep(10)
        #     await domain_entity.info()
        #     print('IP-адрес не найден. Ожидаем.')
        #
        # print('IP:', domain_entity.guest_agent.first_ipv4_ip)
        #
        # # Задание hostname
        # action_response = await domain_entity.set_hostname()
        # action_task = action_response.task
        # task_completed = False
        # while not task_completed:
        #     print('Задача задания hostname ВМ еще не выполнена. Ждем 5 сек.')
        #     await asyncio.sleep(5)
        #     task_completed = await action_task.completed

        # Заведение в домен
        print('Заведение в домен.')
        response = await domain_entity.guest_command(veil_cmd=VeilGuestAgentCmd.MEMORY_STATS)
        print('response:', response.data)

uvloop.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
