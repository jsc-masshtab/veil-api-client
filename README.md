[![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Coverage](https://img.shields.io/static/v1?label=coverage&message=70%&color=yellow)](https://coverage.readthedocs.io/en/coverage-5.1/)

# VeiL api client 
Предназначен для упрощения интеграции между конечным приложением/скриптом и ECP VeiL. Если вы не хотите слишком глубоко 
погружаться в детали и нюансы работы с сессиями, сущностями и конечным API VeiL - рассмотрите работу через данную 
библиотеку. Внутри мы используем **aiohttp client**.

## Установка
Проект доступен в PyPi, можете воспользоваться поддерживаемым пакетным менеджером, например, **pip**

`pip install veil-api-client`

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
from veil_api_client import VeilCacheConfiguration, VeilRetryConfiguration 

# Сущность пагинатора в ответе
from veil_api_client import VeilRestPaginator

# Интерфейсы для аргументов сущностей на VeiL ECP
from veil_api_client import DomainConfiguration, VeilGuestAgentCmd, DomainTcpUsb
```

### Разовый запуск
Если ваш сценарий использования это асинхронный скрипт, который должен выполниться и завершить свою работу,
то лучше всего использовать менеджер контекста. 

Например, Вам нужно получить список из 10 ВМ на ECP VeiL и для каждой выполнить команду start:
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

#### Примеры использования тэгов
```
# Список тэгов
tags_response = await session.tag().list()

# Создание тэга
new_tag1 = TagConfiguration(verbose_name='tag9', slug='tag9_slug')
tag1_response = await session.tag().create(new_tag1)
if tag1_response.success:
    task = tag1_response.task  # Таска создания нового тега
    new_uid = task.first_entity  # идентификатор создаваемой сущности

# Информация по тэгу
tag_response = await session.tag(new_uid).info()
# Сущность тега
tag = tag_response.response[0]

# Прикрепление сущности к тэгу
entity = VeilEntityConfiguration(entity_uuid='01747df8-bdc6-4a50-9747-3e59ef5d4868',
                                 entity_class='domain')
entity_response = await tag.add_entity(entity_configuration=entity)
if entity_response.success:
    print('Успешное прикрепление')

# Прикрепление нескольких сущностей к тэгу
entity1 = VeilEntityConfiguration(entity_uuid='01747df8-bdc6-4a50-9747-3e59ef5d4868',
                                  entity_class='domain')
entity2 = VeilEntityConfiguration(entity_uuid='67e45225-db3f-4474-b334-e8d83ef89a2a',
                                  entity_class='domain')
entity_response = await tag.add_entities(entities_conf=[entity1, entity2])
if entity_response.success:
     print('Успешное множественное прикрепление')

# Редактирование тэга
update_response = await tag.update(colour='#ff0000', verbose_name='newname')
if update_response.success:
     print('Успешное редактирование')

# Открепление сущности от тэга
tag = session.tag('581d2c2b-1f1b-4807-953a-c0e80e8a943b')
await tag.info()#
entity = VeilEntityConfiguration(entity_uuid='01747df8-bdc6-4a50-9747-3e59ef5d4868',
                                 entity_class='domain')

entity_response = await tag.remove_entity(entity_configuration=entity)
if entity_response.success:
    print('Успешное открепление')

# Открепление сущностей от тэга
tag = session.tag('3cacf9f1-7107-45de-bd9d-55d8d6e7eeb3')
await tag.info()
entity1 = VeilEntityConfiguration(entity_uuid='01747df8-bdc6-4a50-9747-3e59ef5d4868',
                                  entity_class='domain')
entity2 = VeilEntityConfiguration(entity_uuid='67e45225-db3f-4474-b334-e8d83ef89a2a',
                                  entity_class='domain')
entity_response = await tag.remove_entities(entities_conf=[entity1, entity2])
if entity_response.success:
     print('Успешное множественное открепление')

# Удаление
remove_response = await tag.remove()
if remove_response.success:
     print('Успешное удаление')
```

### Пример для изменения золотого образа (шаблона)
```
domain = session.domain('67e45225-db3f-4474-b334-e8d83ef89a2a')
await domain.change_template()
```

### Постоянно запущенное приложение
Если ваше приложение запущено постоянно и ему необходима +- постоянная связь с VeiL ECP, стоит доработать 
**VeilClientSingleton**. Основное отличие этого сценария - будет храниться ранее созданный инстанс клиента для 
конкретного контроллера. Это сократит возможные дублирования сессий, временные затраты на установку соединения 
для запросов с маленьким временным интервалом и унифицирует настройки. 
При таком сценарии использования — слежение за закрытием сессий перекладывается на ваше приложение.
Если этот сценарий Вам кажется ближе, задумайтесь о расширении готовой логики VeilClientSingleton. 

Ниже пример, который может пригодиться:
```
import asyncio
import json
import uvloop
import logging
from typing import Optional

from pymemcache.client.base import Client as MemcachedClient
from veil_api_client import (VeilClient, VeilClientSingleton,
                             VeilRetryConfiguration, VeilCacheConfiguration, VeilDomainExt,
                             VeilCacheAbstractClient)

logging.basicConfig(level=logging.DEBUG)


# Длинная часть с переопределением и дополнением базовой логики
class DictSerde:
    """Сериализатор для записи данных ответов в кэш."""

    @staticmethod
    def serialize(key, value):
        """Serialize VeilApiResponse to bytes."""
        if isinstance(value, str):
            return value.encode('utf-8'), 1
        elif isinstance(value, dict):
            return json.dumps(value).encode('utf-8'), 2
        raise Exception('Unknown serialization format')

    @staticmethod
    def deserialize(key, value, flags):
        """Deserialize bytes to dict."""
        if flags == 1:
            return value.decode('utf-8')
        elif flags == 2:
            return json.loads(value.decode('utf-8'))
        raise Exception('Unknown serialization format')


class UserCacheClient(VeilCacheAbstractClient):
    """Реализация пользовательского кэш-клиента."""

    def __init__(self):
        self.client = MemcachedClient(server=('localhost', 11211), serde=DictSerde())

    async def get_from_cache(self,
                             veil_api_client_request_cor,
                             veil_api_client,
                             method_name,
                             url: str,
                             headers: dict,
                             params: dict,
                             ssl: bool,
                             json_data: Optional[dict] = None,
                             retry_opts: Optional[VeilRetryConfiguration] = None,
                             ttl: int = 0,
                             *args, **kwargs):
        """Метод, который вызовет клиент.

        Внутри себя должен вызывать запись в кэш и чтение из кэша.
        """
        # cache key can`t contain spaces
        cache_key = url.replace(' ', '')
        # Получаем данные из кэша
        cached_result = self.client.get(cache_key)
        # Если данные есть - возвращаем
        if cached_result:
            return cached_result
        # Если в кэше нет актуальных данных - получаем результат запроса
        result_dict = await veil_api_client_request_cor(veil_api_client,
                                                        method_name, url, headers,
                                                        params, ssl, json_data,
                                                        retry_opts, *args, **kwargs)
        # Т.к. ответ преобразуется в VeilApiResponse после вызова этого метода в result_dict будет лежать ответ aiohttp
        if isinstance(result_dict, dict) and result_dict.get('status_code', 0) in (200, 201, 202, 204):
            try:
                # пытаемся сохранить результат в кэш
                await self.save_to_cache(cache_key, result_dict, ttl)
            except Exception as ex_msg:
                print('Failed to save response to cache: {}'.format(ex_msg))
        # Возвращаем ответ aiohttp
        return result_dict

    async def save_to_cache(self, key, data, ttl: int):
        """Сохраняем результат в кэш."""
        return self.client.set(key, data, expire=ttl)


class UserRequestError(AssertionError):
    pass


class UserDomain:

    @staticmethod
    async def get(id_):
        return {'key': 'value {}'.format(id_)}


class UserVeilClient(VeilClient):
    """Переопределяем встроенный клиент."""

    async def api_request(self, *args, **kwargs):

        response = await super().api_request(*args, **kwargs)
        if not hasattr(response, 'status_code'):
            raise ValueError('Response is broken. Check veil_api_client version.')

        url = kwargs.get('url')
        params = kwargs.get('params')
        api_object = kwargs.get('api_object')

        if hasattr(api_object, 'api_object_id') and api_object.api_object_id:
            if response.status_code == 404 and isinstance(api_object, VeilDomainExt):
                vm_object = await UserDomain.get(api_object.api_object_id)
                print('vm object:', vm_object.items())

        if not response.success:
            error_description = 'url: {}\nparams: {}\nresponse:{}'.format(url, params, response.data)
            raise UserRequestError(error_description)

        return response


class UserVeilClientSingleton(VeilClientSingleton):
    """Переопределяем менеджер соединений."""

    __client_instances = dict()

    def __init__(self) -> None:
        """Please see help(VeilClientSingleton) for more info."""
        self.__TIMEOUT = 10
        self.__CACHE_OPTS = VeilCacheConfiguration(ttl=30, cache_client=UserCacheClient())
        self.__RETRY_OPTS = VeilRetryConfiguration()

    def add_client(self, server_address: str, token: str, retry_opts=None) -> 'VeilClient':
        """Пре конфигурированное подключение."""

        if server_address not in self.__client_instances:
            instance = UserVeilClient(server_address=server_address,
                                      token=token,
                                      session_reopen=True,
                                      timeout=self.__TIMEOUT,
                                      ujson_=True,
                                      cache_opts=self.__CACHE_OPTS,
                                      retry_opts=self.__RETRY_OPTS)
            self.__client_instances[server_address] = instance
        return self.__client_instances[server_address]

    @property
    def instances(self) -> dict:
        """Show all instances of VeilClient."""
        return self.__client_instances


# Конец переопределения и начало клиента
async def extra_main():
    token = 'jwt eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6ImRldnlhdGtpbl92ZGkiLCJleHAiOjE5MjY2Nzk4OTUsInNzbyI6ZmFsc2UsIm9yaWdfaWF0IjoxNjEyMTgzODk1fQ.UKf7Sr4JB6tQw8Ftn5Cex0ZO6Qg4uNG24827fohWVXM'
    server = '192.168.11.102'

    # Настраиваем клиент для будущего использования
    # При проверке статуса проверяется именно тот статус, который пришел в ответе. Предположим мы хотим повторы для всех
    # вм, что не удалось найти
    veil_client = UserVeilClientSingleton()

    # Добавляем подключение к первому контроллеру
    session1 = veil_client.add_client(server, token)

    # Получаем информацию о конкретной ВМ
    veil_domain = session1.domain()
    await veil_domain.list()

    # Берем ответы из кеша
    await veil_domain.list()
    await veil_domain.list()
    await veil_domain.list()
    await veil_domain.list()

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
изменить, например, по умолчанию в библиотеке используется ujson, поэтому если Вы расширяете написанные методы, 
имейте в виду ограничения, которые он накладывает, либо переопределите опцию ujson_ на False.

## Сущности, к которым предоставляется доступ и их методы
Любой объект клиента имеет интерфейсы:
* Кластер - VeilClient.cluster()
* Контроллер - VeilClient.controller()
* Пул данных - VeilClient.data_pool()
* Домен (Виртуальная машина) - VeilClient.domain()
* Нода (узел, сервер) - VeilClient.node()
* Задача - VeilClient.task()
* Виртуальный диск - VeilClient.vdisk()
* Тэг - VeilClient.tag()
* Библиотека - VeilClient.library()
* Журнал - VeilClient.event()

Если при инициализации сущности не был передан id сущности, то есть возможность работы только с обобщенными методами
вроде list(). Если вы хотите иметь доступ к методам конкретной сущности — необходимо указать ее id.

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

### Параметры для подключения SPICE/VNC
Сущность **VeilDomainExt** обладает двумя интерфейсами для получения данных подключения к ВМ.
Результатом выполнения обоих методов будет инстанс *DomainRemoteConnectionConfiguration* со следующими атрибутами:
* connection_url - "сырой" url, который вернул контроллер
* connection_type - тип соединения (VNC/SPICE)
* host - **host**-часть из аргументов запроса в **connection_url**
* password - **password**-часть из аргументов запроса в **connection_url**
* token - **token**-часть из аргументов запроса в **connection_url** (внутри **path**)

#### SPICE
```spice = await domain.spice_conn()```

#### VNC
```vnc = await domain.vnc_conn()```
        
        

### Основные конфигурируемые параметры VeilClient:
* server_address - адрес контроллера VeiL (без указания протокола, мы сами подставим https)
* token - токен интеграции VeiL
* session_reopen - автоматически открывать сессию aiohttp.ClientSession, если она закрыта.
* timeout - aiohttp.ClientSession общий таймаут
* extra_headers - дополнительные заголовки для сессии (расширяющие или переопределяющие стандартные заголовки)
* extra_params - дополнительные параметры запроса для сессии (расширяющие или переопределяющие стандартные параметры)
* ujson_ - использовать или нет ujson, или json, опции aiohttp.client. Если в запросах проблемы, попробуйте отключить

### Конфигурируемые параметры VeilClientSingleton:
Мы намеренно сократили конфигурируемые параметры для данного класса, в целях облегчения и оптимизации запросов. Если
вы хотите что-то расширить - сделайте собственный класс по аналогии либо запросите доработку через issue.

* server_address - адрес контроллера VeiL (без указания протокола, мы сами подставим https)
* token - токен интеграции VeiL
* timeout - aiohttp.ClientSession общий таймаут
* cache_opts - VeilCacheConfiguration
* retry_opts - VeilRetryConfiguration

### %Configuration
Для дополнительной валидации (и из-за отсутствия дата классов) конфигурируемые параметры вынесены в отдельные 
классы-потомки супер-класса VeilAbstractConfiguration. Ниже идет их перечисление.

#### VeilCacheConfiguration
Возможность передать пользовательский кэш.
* cache_client: инстанс пользовательского кэш-клиента, который сохраняет и читает данные из кэша.
* ttl: срок хранения данных в кэше. Если указать 0 - кэш не будет использоваться.

#### VeilRetryConfiguration
Опции для повторов запросов. Если указаны, клиент будет автоматически выполнять повтор по условиям описанным ниже.

* num_of_attempts - количество повторов
* timeout - время ожидания перед повтором (с экспоненциальным ростом)
* max_timeout - максимальное время ожидания между попытками
* timeout_increase_step - шаг увеличения времени ожидания
* status_codes - статусы ответа запросов для повторов
* exceptions - исключения ответа запросов для повторов

#### VeilEntityConfiguration
Структура VeiL ECP для доступа к сущностям.

* entity_uuid - уникальный идентификатор сущности.
* entity_class - тип сущности (пул данных, вм и т.п.)

#### TagConfiguration
Упрощенное описание сущности Tag на VeiL ECP.

* verbose_name - не уникальная строка
* slug - уникальная строка
* colour - строка содержащая hex-представление цвета

#### VeilRestPaginator
Упрощенный интерфейс доступа к пагинатору VeiL ECP>

* name - поле **name**
* ordering - порядок сортировки
* limit - ограничение на количество записей в выдаче
* offset - смещение блоков выдачи

#### DomainBackupConfiguration
Параметры для создания бэкапа виртуальной машины на VeiL ECP.

* backup - идентификатор предыдущего бэкапа.
* datapool - идентификатор пула данных на котором будет выполнено хранение 
  (может быть указан только если не передан backup).
* can_be_incremental - атрибут указывающий на возможность инкремента в будущем.
* increment - инкрементировать последний созданных бэкап.
* exclude_iso - исключить из бэкапа подключенные ISO-образы к виртуальной машины.

#### DomainConfiguration
Упрощенное описание параметров копирования виртуальной машины (domain) на VeiL ECP.
*Используется как аргумент domain_configuration в методе **VeilDomainExt.create***

* verbose_name - имя создаваемой ВМ.
* resource_pool - пул ресурсов VeiL ECP для создания ВМ.
* node - узел VeiL ECP для создания ВМ.
* datapool - пул данных VeiL ECP для создания ВМ.
* parent - шаблон VeiL ECP на основе которого необходимо выполнить копирование ВМ.
* thin - новая ВМ будет являться тонким клоном ее родителя.
* count - количество ВМ для создания

#### DomainCloneConfiguration
Упрощенное описание параметров клонирования виртуальной машины (domain) на VeiL ECP.
*Используется как аргумент domain_configuration в методе **VeilDomainExt.clone***

* verbose_name - имя создаваемой ВМ.
* resource_pool - пул ресурсов VeiL ECP для создания ВМ.
* node - узел VeiL ECP для создания ВМ.
* datapool - пул данных VeiL ECP для создания ВМ.
* snapshot - шаблон VeiL ECP на основе которого необходимо выполнить копирование ВМ.
* count - количество ВМ для создания
* start_on - включить создаваемые ВМ

#### DomainUpdateConfiguration
Упрощенное описание параметров редактирования виртуальной машины (domain) на VeiL ECP.

*Используется как аргумент domain_update_configuration в методе **VeilDomainExt.update***

* verbose_name - новое имя.
* description - новое описание.
* os_type - новый тип ОС.
* os_version - новая версия ОС.
* tablet - признак tablet.
* start_on_boot - признак start_on_boot.
* spice_stream - признак spice_stream.

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
* paginator_count - count из ответа пагинатора, актуально для запросов вида list()
* paginator_next - url следующей страницы с ответами пагинатора, актуально для запросов вида list()
* paginator_previous - url предыдущей страницы с ответами пагинатора, актуально для запросов вида list()

## Как принять участие в проекте
Форк -> изменения в отдельной ветке -> запустите тесты и разместите PR/MR.