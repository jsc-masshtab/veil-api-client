[![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)


## Примечание
veil-api-client не пытается анализировать ошибки возвращаемые VeiL. Например, если токен авторизации некорректен и 
VeiL вернет 401, то veil-api-client просто ретранслирует ответ дальше. Прерывания исполнения не будет.
В клиент токен должен передаваться уже с jwt. Сам тип токена хранится в payload токена и разбирается клиентом при сохранении.

## Список идемпадентных запросов

## Откуда брать коды ошибок VeiL
## Примеры вызова
Скорее всего вы захотите использовать клиент в паре с uvloop.
Использовать клиент лучше через менеджер контекста:
```
async with HttpsApiClient(server_address=server_address, token=token) as session:
    domain = session.domain()
    domain2 = session.domain('a3e02ced-037f-41ab-b0bb-61771ae00b40')

    domains_list_response = await domain.list()

    domain_info_response = await domain2.info()
    domain_start_response = await domain2.start()

    domain.api_object_id = 'a3e02ced-037f-41ab-b0bb-61771ae00b40'
    domain_info_response2 = await domain.info()

    domain_remote_response = await domain.remote_access(enable=False)
    domain_remote_response = await domain.remote_access(enable=False)

    print(domains_list_response.status_code)
    print(domains_list_response.json)

    print(domain_info_response.status_code)
    print(domain_info_response.json)

    print(domain_start_response.status_code)
    print(domain_start_response.json)

    print(domain_info_response2.status_code)

    print(domain_remote_response.status_code)
    print(domain_remote_response.json)
```
Но если этот вариант не подходит - не забудьте закрыть сессию.
```
session = HttpsApiClient(server_address=server_address, token=token)
response = await session.domain().list()
print(response.status_code)
print(response.json)
await session.close()
```    

## Установка
`pip install veil_api_client-2.0.0-py3-none-any.whl` 
