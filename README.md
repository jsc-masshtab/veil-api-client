[![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Coverage](https://img.shields.io/static/v1?label=coverage&message=49%&color=red)](https://coverage.readthedocs.io/en/coverage-5.1/)

# VeiL api client 
Предназначен для упрощения интеграции между конечным приложением/скриптом и ECP VeiL. Если вы не хотите слишком глубоко 
погружаться в детали и нюансы работы с сессиями, сущностями и конечным API VeiL - рассмотрите работу через данную 
библиотеку. Внутри мы используем **aiohttp client**.

## Установка
В ближайшее время библиотека должна стать доступной через pypi, но на данный момент самый простой способ установки это
выполнить установку через pip указав gitlab-репозиторий:
`pip install git+http://gitlab.bazalt.team/vdi/veil-api-client`

## Использование
Предусмотрено два возможных сценария использования: постоянная работа и разовый запуск с завершением. Ниже будет пример
простого и продвинутого использования.

### Документация
Краткое описание вы читаете сейчас, более подробное доступна через help, например, help(response).
Логика импортов построена так, что конечные сущности с которыми предлагается работать доступны напрямую из корня.
Краткое описание классов ниже:
```
# Сущности клиента
from veil_api_client import VeilClient, VeilClientSingleton 

# Дополнительные параметры клиента для продвинутого использования
from veil_api_client import VeilCacheOptions, VeilRetryOptions 

# Сущность пагинатора в ответе
from veil_api_client import VeilRestPaginator

# Интерфейсы для аргументов сущностей на VeiL ECP
from veil_api_client import DomainConfiguration, VeilGuestAgentCmd, DomainTcpUsb, VeilDomain  
```

### Разовый запуск
Если ваш сценарий использования это асинхронный скрипт, который должен выполниться и завершить свою работу,
то лучше всего использовать менеджер контекста. 

Например, Вам нужно получить список из 10 ВМ на ECP VeiL и для каждой выполнить комманду start:
```
import asyncio
from veil_api_client import VeilClient, VeilRestPaginator
logging.basicConfig(level=logging.DEBUG)  # debug message can be useful

token_115 = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2V'
server_address_115 = '192.168.11.115'

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

loop = asyncio.get_event_loop()
loop.run_until_complete(simple_main())
```

### Постоянно запущенное приложение
Если ваше приложение запущено постоянно и ему необходима +- постоянная связь с VeiL ECP, стоит доработать 
**VeilClientSingleton**. Основное отличие этого сценария - будет храниться ранее созданный инстанс клиента для 
конкретного контроллера. Это сократит возможные дублирования сессий, временные затраты на установку соединения 
для запросов с маленьким временным интервалом и унифицирует настройки. 
При таком сценарии использования - слежение за закрытием сессий перекладывается на ваше приложение.
Если этот сценарий Вам кажется ближе, задумайтесь о расширении готовой логики VeilClientSingleton собственной. 

Ниже пример, который может пригодиться:
```
import asyncio
import uvloop
import logging

from veil_api_client import VeilClient, VeilClientSingleton, VeilCacheOptions, VeilDomain


async def extra_main():
    # Меняем встроенную логику на ту, что больше подходит для собственных нужд
    class VmNotFoundError(AssertionError):
        pass

    class YobaVeilClient(VeilClient):
        """Отвечает за сетевое взаимодействие с ECP VeiL."""

        async def get(self, api_object, url, extra_params):
            """Переопределен для перехвата окончательного статуса ответов."""
            response = await super().get(api_object=api_object, url=url, extra_params=extra_params)
            if hasattr(response, 'status_code') and hasattr(api_object, 'api_object_id') and api_object.api_object_id:
                if response.status_code == 404 and isinstance(api_object, VeilDomain):
                    raise VmNotFoundError('Vm not found!')
            return response

    class YobaVeilClientSingleton(VeilClientSingleton):
        """Хранит ранее инициализированные подключения."""

        __client_instances = dict()

        def __init__(self, retry_opts=None) -> None:
            """Please see help(VeilClientSingleton) for more info."""
            self.__TIMEOUT = 10
            self.__CACHE_OPTS = VeilCacheOptions(ttl=10, cache_type='memcached',
                                                 server='127.0.0.1')
            self.__RETRY_OPTS = retry_opts

        def add_client(self, server_address: str, token: str, retry_opts=None) -> 'VeilClient':
            """Преконфигурированное подключение."""
            if server_address not in self.__client_instances:
                instance = YobaVeilClient(server_address=server_address, token=token,
                                          session_reopen=True, timeout=self.__TIMEOUT, ujson_=True,
                                          cache_opts=self.__CACHE_OPTS,
                                          retry_opts=self.__RETRY_OPTS)
                self.__client_instances[server_address] = instance
            return self.__client_instances[server_address]

        @property
        def instances(self) -> dict:
            """Show all instances of VeilClient."""
            return self.__client_instances
    
    # Настраиваем клиент для будущего использования    
    # При проверке статуса проверяется именно тот статус, который пришел в ответе. Предположим мы хотим повторы для всех
    # вм, что не удалось найти
    veil_client = YobaVeilClientSingleton(
        VeilRetryOptions(status_codes={404}, timeout_increase_step=5, num_of_attempts=3))

    # Добавляем подключение к первому контроллеру
    session1 = veil_client.add_client(server, token)
    
    #  Начинаем пользоваться
    # Получаем информацию о конкретной ВМ
    veil_domain = session1.domain('998131cc-9516-44cc-9718-55c8ea14cde6')
    await veil_domain.info()

    # Берем ответы из кеша
    await veil_domain.info()
    await veil_domain.info()
    await veil_domain.info()
    await veil_domain.info()

    # Добавляем еще одно подключение к контроллеру
    # В результате у session2 будет ссылка на тот же клиент, что передан для session
    session2 = veil_client.add_client(server, token)

    # Перед завершением приложения закрываем все используемые сессии
    instances = veil_client.instances
    for inst in instances:
        await instances[inst].close()

uvloop.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(extra_main())
```


## Конфигурация
Если вам потребовалось использовать сетевые запросы, то с большой долей вероятности Вы захотите использовать uvloop.
Пример установки можно посмотреть [тут](https://github.com/MagicStack/uvloop)
Большинство значений передаваемых по умолчанию являются оптимальными настройками VeiL VDI, однако может потребоваться их
изменить, например, по умолчанию в библиотеке используется ujson, поэтому если Вы расширяете написанные методы имейте 
ввиду ограничения, которые он накладывает, либо переопределите опцию ujson_ на False.

## Сущности, к которым предоставляется доступ и их методы
любой инстанс клиента предоставляет доступ к следующим сущностям:
* Кластер - VeilClient.cluster()
* Контроллер - VeilClient.controller()
* Датапул - VeilClient.data_pool()
* Домен (Виртуальная машина) - VeilClient.domain()
* Нода (узел, сервер) - VeilClient.node()
* Задача - VeilClient.task()
* Виртуальный диск - VeilClient.vdisk()
Если при инициализации сущности не был передан id сущности, то есть возможность работы только с обобщенными методами
вроде list(). Если вы хотите иметь доступ к методам конкретной сущности - необходимо указать ее id.

### Основные методы сущностей
* list() - асинхронный метод для получения списка сущностей на VeiL, использует переопределяемый пагинатор. Если сущностей
больше 100 - вам необходимо самостоятельно настроить limit для пагинатора, иначе будет 100. 
* info() - получение информации о конкретной сущности. После вызова этого метода Вы можете использовать как атрибут *.value*
так и конкретные атрибуты у сущности, например domain.service
* public_attrs - список всех публичных атрибутов. После получения info они будут обновлены.
* uuid_ - конвертирует str с id в uuid.
* creating - результат операция сравнения статуса сущности
* active - результат операция сравнения статуса сущности
* failed - результат операция сравнения статуса сущности
* deleting - результат операция сравнения статуса сущности
* service - результат операция сравнения статуса сущности
* partial - результат операция сравнения статуса сущности

### Основные конфигурируемые параметры VeilClient:
* server_address - адрес контроллера VeiL (без указания протокола, мы сами подставим https)
* token - токен интеграции VeiL
* session_reopen - автоматически открывать сессию aiohttp.ClientSession, если она закрыта.
* timeout - aiohttp.ClientSession общий таймаут
* extra_headers - дополнительные заголовки для сессии (расширяющие или переопределяющие стандартные заголовки)
* extra_params - дополнительные параметры запроса для сессии (расширяющие или переопределяющие стандартные параметры)
* ujson_ - использовать или нет ujson или json, опции aiohttp.client. Если в запросах проблемы, попробуйте отключить

### Конфигурируемые параметры VeilClientSingleton:
Мы намеренно сократили конфигурируемые параметры для данного класса, в целях облегчения и оптимизации запросов. Если
вы хотите что-то расширить - сделайте собственный класс по аналогии либо запросите доработку через issue.

* server_address - адрес контроллера VeiL (без указания протокола, мы сами подставим https)
* token - токен интеграции VeiL
* timeout - aiohttp.ClientSession общий таймаут
* cache_opts - VeilCacheOptions
* retry_opts - VeilRetryOptions

#### VeilCacheOptions
Минимальное кеширование ответов. Скорее всего будет исключено из пакета, т.к. настройки кеширования очень своеобразная
опция.
* cache_type - тип используемого кэша
* server - адрес подключения к хранилищу кэша
* ttl - время жизни записи в кэше

#### VeilRetryOptions
num_of_attempts - количество повторов
timeout - время ожидания перед повтором (с экспоненциальным ростом)
max_timeout - максимальное время ожидания между попытками
timeout_increase_step - шаг увеличения времени ожидания
status_codes - статусы ответа запросов для повторов
exceptions - исключения ответа запросов для повторов

### Основные атрибуты сущностей
* api_object_prefix - указывает к какой сущности мы будем обращаться на VeiL ECP
* api_object_id - идентификатор сущности на VeiL ECP, обычно UUID4

### Основные атрибуты ответа (VeilApiResponse)
* data - стандартный атрибут aiohttp.client
* status_code - стандартный атрибут aiohttp.client
* headers - стандартный атрибут aiohttp.client
* success - признак успешности запроса (статус коды 200, 201, 202, 204)
* task - если запрос был поставлен в очередь на VeiL ECP тут будет сущность задачи, которую можно ожидать
* response - список 1-М сущностей к которым происходило обращение
* error_code - код ошибки на VeiL, если запрос успешен, код будет 0
* error_detail - текстовое сопровождение ошибки на VeiL

## Как принять участие в проекте
Сделайте форк, внесите свои изменения в отдельной ветке, внесите свои изменения, запустите тесты и разместите PR/MR.