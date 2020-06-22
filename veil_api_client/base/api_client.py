# -*- coding: utf-8 -*-
"""Veil api client."""
from types import TracebackType
from typing import Dict, Optional, Type
from uuid import uuid4

import aiohttp

from .api_response import VeilApiResponse
from .utils import NullableDictType, VeilJwtTokenType, VeilUrlStringType

# TODO: отслеживание кук
# TODO: check sessions count on Veil
# TODO: max retries must be configurable param


class VeilApiClient:
    """Base class for veil api client."""

    __AUTH_HEADER_KEY = 'Authorization'
    __USER_AGENT_VAL = 'veil-api-client/2.0'
    __IDEMPOTENCY_HEADER_KEY = 'Idempotency-Key'
    __extra_headers = NullableDictType('__extra_headers')
    __extra_params = NullableDictType('__extra_params')

    server_address = VeilUrlStringType('server_address')
    token = VeilJwtTokenType('token')

    def __init__(self, server_address: str, token: str, transfer_protocol: str, ssl_enabled: bool = True,
                 session_reopen: bool = False, timeout: int = 5 * 60, extra_headers: dict = None,
                 extra_params: dict = None
                 ):
        """Конструктор для сессии с VeiL."""
        self.server_address = server_address
        self.token = token
        self.__session_reopen = session_reopen
        self.__ssl_enabled = ssl_enabled
        self.__transfer_protocol_prefix = transfer_protocol
        self.__extra_headers = extra_headers
        self.__extra_params = extra_params

        __timeout = aiohttp.ClientTimeout(total=timeout)
        self.__timeout = __timeout
        self.__session = aiohttp.ClientSession(timeout=__timeout)

    async def __aenter__(self) -> 'VeilApiClient':
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None:
        await self.__session.close()

    async def close(self) -> None:
        await self.__session.close()

    @property
    def base_url(self):
        return ''.join([self.__transfer_protocol_prefix, self.server_address, '/api/'])

    @property
    def __base_params(self) -> Dict:
        return {'async': 1}

    @property
    def __params(self) -> Dict:
        """Расширяем стандатный набор параметров переданными пользователем."""
        params = self.__base_params
        if self.__extra_params and isinstance(self.__extra_params, dict):
            params.update(self.__extra_params)
        return params

    @property
    def __base_headers(self) -> Dict:
        headers_dict = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'User-Agent': self.__USER_AGENT_VAL,
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Accept-Language': 'en',
            self.__AUTH_HEADER_KEY: '{}'.format(self.token),
            self.__IDEMPOTENCY_HEADER_KEY: '{}'.format(uuid4())
        }
        return headers_dict

    @property
    def __headers(self) -> Dict:
        """Расширяем стандатный набор заголовков переданными пользователем."""
        headers = self.__base_headers
        if self.__extra_headers and isinstance(self.__extra_headers, dict):
            headers.update(self.__extra_headers)
        return headers

    async def get(self, url) -> VeilApiResponse:
        """Отправить get запрос на VeiL ECP."""
        if self.__session.closed and self.__session_reopen:
            self.__session = aiohttp.ClientSession()

        resp = await self.__session.get(url,
                                        headers=self.__headers,
                                        params=self.__params,
                                        ssl=self.__ssl_enabled)
        status_code = resp.status
        data = await resp.json()
        headers = resp.headers
        return VeilApiResponse(status_code=status_code, data=data, headers=headers)

    async def post(self, url, json=None) -> VeilApiResponse:
        """Отправить get запрос на VeiL ECP."""
        if self.__session.closed and self.__session_reopen:
            self.__session = aiohttp.ClientSession(self.__timeout)

        resp = await self.__session.post(url,
                                         headers=self.__headers,
                                         params=self.__params,
                                         ssl=self.__ssl_enabled,
                                         json=json)
        status_code = resp.status
        data = await resp.json()
        headers = resp.headers
        return VeilApiResponse(status_code=status_code, data=data, headers=headers)
