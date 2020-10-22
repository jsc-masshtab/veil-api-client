# -*- coding: utf-8 -*-
"""Temporary runner."""
import asyncio
import uvloop
from enum import IntEnum
import logging

from veil_api_client import VeilClient, VeilCacheOptions, DomainConfiguration, VeilGuestAgentCmd, DomainTcpUsb, VeilRetryOptions

# TODO: побороть кривые импорты
# TODO: tests - доработать по отчету coverage
# TODO: api_object_prefix - в README указать, что это путь к сущности на ECP
# TODO: description - документация
# TODO: retry
# TODO: описать как подключить собственный кеш на примере redis?
logging.basicConfig(level=logging.DEBUG)


class VmPowerState(IntEnum):
    """Veil domain power states."""

    UNDEFINED = 0
    OFF = 1
    SUSPENDED = 2
    ON = 3


async def main():
    """Примеры использования."""
    token1 = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo4LCJ1c2VybmFtZSI6InZkaV85a2luIiwiZXhwIjoxOTE3MjcwMDU5LCJzc28iOmZhbHNlLCJvcmlnX2lhdCI6MTYwMjc3NDA1OX0.ZXbVFPHXE1oblEmWRnVY4FNROu0QAzDjTdbRXL2itIs'
    token2 = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjAzMzcyNzQ5LCJzc28iOmZhbHNlLCJvcmlnX2lhdCI6MTYwMzI4NjM0OX0.RrYDLZoqjjkRxuLnV6NEQeEVljtuvHravn1IophDlcI'
    server1 = '192.168.11.115'

    async with VeilClient(token=token2, server_address=server1) as client:
        veil_controller = client.controller()
        try:
            print(await veil_controller.base_version())
        except Exception as E:
            print(E)

        # ids_set = {'907e3335-4f6b-4de9-a9ef-be0253befb71','f8f057af-f846-4c03-a46b-556bb662faac'}
        # ids_str = ','.join(ids_set)
        ids_str = "907e3335-4f6b-4de9-a9ef-be0253befb71,"
        # TODO: убрать лишнюю запятую
        domains_list_response = await client.domain().list(fields=['id', 'user_power_state'],
                                                  params={
                                                          'ids': str(ids_str)})
        print('domains list:', domains_list_response.paginator_results[0].get('id'))
    # cache_options = VeilCacheOptions(ttl=10, cache_type='memcached', server=('localhost', 11211))a

    # пример про заведение в домен
    # async with VeilClient(server1, token1) as veil_single:
    #     domain_client = veil_single.domain('1555350a-5f04-46c9-95e2-43c573c190ea')
    #     # Получаем состояние параметров ВМ
    #     domain_response = await domain_client.info()
    #     powered = domain_client.powered
    #     print('VM is powered:', powered)
    #     # Проверяем настройки удаленного доступа
    #     # if not domain_client.remote_access:
    #     #     action_response = await domain_client.enable_remote_access()
    #     #     action_task = action_response.task
    #     #     task_completed = False
    #     #     while not task_completed:
    #     #         print('Задача еще не выполнена. Ждем 5 сек.')
    #     #         await asyncio.sleep(5)
    #     #         task_completed = await action_task.finished
    #     #     print('Зачада выполнена.')
    #     #     print('Обновляем параметры ВМ')
    #     #     await domain_client.info()
    #     #
    #     # # Проверяем включена ли ВМ
    #     # print('Domain power state:', domain_client.power_state)
    #     # if not domain_client.power_state == VmPowerState.ON:
    #     #     print('ВМ выключена - нужно ее включить.')
    #     #     action_response = await domain_client.start()
    #     #     action_task = action_response.task
    #     #     task_completed = False
    #     #     while not task_completed:
    #     #         print('Задача включения ВМ еще не выполнена. Ждем 3 сек.')
    #     #         await asyncio.sleep(3)
    #     #         task_completed = await action_task.finished
    #     #     print('Зачада выполнена.')
    #     #     print('Обновляем параметры ВМ')
    #     #     await domain_client.info()
    #     #
    #     # # Ожидаем доступности гостевого агента.
    #     # while not domain_client.guest_agent.qemu_state:
    #     #     await asyncio.sleep(5)
    #     #     await domain_client.info()
    #     #     print('Гостевой агент недоступен. Ждем еще.')
    #     #
    #     # # Для подключения по rdp ВМ нужен как минимум 1 ip-адрес
    #     # while not domain_client.hostname:
    #     #     await asyncio.sleep(10)
    #     #     await domain_client.info()
    #     #     print('IP-адрес не найден. Ожидаем.')
    #     #
    #     # print('IP:', domain_client.guest_agent.first_ipv4_ip)
    #     #
    #     # # Задание hostname
    #     # print('domain hostname:', domain_client.hostname)
    #     # if not domain_client.hostname:
    #     #     action_response = await domain_client.set_hostname('devyatkin0902-3')
    #     #     action_task = action_response.task
    #     #     task_completed = False
    #     #     while not task_completed:
    #     #         print('Задача задания hostname ВМ еще не выполнена. Ждем 5 сек.')
    #     #         await asyncio.sleep(5)
    #     #         task_completed = await action_task.finished
    #     #
    #     # # Ожидаем доступности гостевого агента.
    #     # while not domain_client.guest_agent.qemu_state:
    #     #     await asyncio.sleep(5)
    #     #     await domain_client.info()
    #     #     print('Гостевой агент недоступен. Ждем еще.')
    #
    #     # # Заведение в домен
    #     # already_in_domain = await domain_client.in_ad
    #     # print('Машина уже в домене:', already_in_domain)
    #     # if not already_in_domain and domain_client.os_windows:
    #     #     print('Заведение в домен.')
    #         action_response = await domain_client.add_to_ad(domain_name='bazalt.team', login='ad120', password='Bazalt1!')
    #     #     action_task = action_response.task
    #     #     task_completed = False
    #     #     while not task_completed:
    #     #         print('Задача заведения в домен еще не выполнена. Ждем 5 сек.')
    #     #         await asyncio.sleep(5)
    #     #         task_completed = await action_task.finished
    #     #
    #     #     task_failed = await action_task.failed
    #     #     if task_failed:
    #     #         print('Задача заведения в домен выполнена с ошибкой:')
    #     #         print(action_task.error_message)
    #     #     else:
    #     #         print('Задача заведения в домен завершена успешно.')
    #     #
    #     # # Ожидаем доступности гостевого агента.
    #     # while not domain_client.guest_agent.qemu_state:
    #     #     await asyncio.sleep(5)
    #     #     await domain_client.info()
    #     #     print('Гостевой агент недоступен. Ждем еще.')
    #
    #     print('Все готово.')
    #     # TODO: протоколирование ошибок

    # пример про usb
    # async with VeilClient(server1, token1) as veil_single:
    #     # Список usb устройств на ноде
    #     # node_client = veil_single.node('0ca1aa55-b1d8-427e-bbf7-9f8ac57db911')
    #     # node_usb_response = await node_client.usb_devices()
    #     # print('raw data:')
    #     # print(node_usb_response.data)
    #
    #     # Присоединение usb для ВМ
    #     domain_client = veil_single.domain('be1ae32b-b10e-460c-a73d-88c97aa685f2')
    #     domain_tcp_usb_params = DomainTcpUsb(host='192.168.6.250', service=17777)
    #     attach_response = await domain_client.attach_usb(action_type='tcp_usb_device', tcp_usb=domain_tcp_usb_params, no_task=True)
    #     print('raw data:')
    #     print(attach_response.data)
    #
    #     resp = await domain_client.detach_usb(action_type='tcp_usb_device', remove_all=True)
    #     print(resp.data)
    #     print(resp.task)

    #     # необязательная часть про задачу
    #     action_task = attach_response.task
    #     task_completed = False
    #     while not task_completed:
    #         print('Задача подключения USB ВМ еще не выполнена. Ждем 3 сек.')
    #         await asyncio.sleep(3)
    #         task_completed = await action_task.finished
    #     print('Зачада выполнена.')
    #     # Отсоединение usb для ВМ
    #     detach_response = await domain_client.detach_usb(action_type='tcp_usb_device', remove_all=True)
    #     print('raw data:')
    #     print(detach_response.data)
    #     # необязательная часть про задачу
    #     action_task = detach_response.task
    #     task_completed = False
    #     while not task_completed:
    #         print('Задача отключения USB ВМ еще не выполнена. Ждем 3 сек.')
    #         await asyncio.sleep(3)
    #         task_completed = await action_task.finished
    #     print('Зачада выполнена.')

    # альтернативная реализация ввода в домен с указанием path

    # retry_options = VeilRetryOptions(status_codes={404}, num_of_attempts=3)
    # print('retry options:', retry_options)
    #
    # async with VeilClient(server1, token1, retry_opts=retry_options) as veil_single:
    #     domain_entity = veil_single.domain('ac138e26-22f2-4c0a-9b2d-f76b5dec56b9')
    #     response = await domain_entity.info()
    #     print('error code:', response.error_code)
    #     print('error detail:', response.error_detail)

uvloop.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
