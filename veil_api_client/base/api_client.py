# -*- coding: utf-8 -*-
"""Veil api client."""
import logging
from types import TracebackType
from typing import Dict, Optional, Type
from uuid import uuid4

try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None

from .api_response import veil_api_response_decorator
from .descriptors import NullableDictType, VeilJwtTokenType, VeilUrlStringType

logger = logging.getLogger('veil-api-client.request')
logger.addHandler(logging.NullHandler())
# TODO: max retries must be configurable param with configuration of observable statuses


class VeilApiClient:
    """Base class for veil api client.

    Private attributes:
        __AUTH_HEADER_KEY: Header authorization key.
        __USER_AGENT_VAL: Header user-agent value.
        __IDEMPOTENCY_HEADER_KEY: Header idempotency key.

    Attributes:
        server_address: VeiL server address (without protocol).
        token: VeiL auth token.
        transfer_protocol: http transfer protocol prefix (now only https).
        ssl_enabled: ssl-certificate validation.
        session_reopen: auto reopen aiohttp.ClientSession when it`s closed.
        timeout: aiohttp.ClientSession total timeout.
        extra_headers: additional user headers.
        extra_params: additional user params.
        cookies: additional user cookies (probably useless).
        json_serialize: aiohttp.ClientSession json serializer.
    """

    __AUTH_HEADER_KEY = 'Authorization'
    __USER_AGENT_VAL = 'veil-api-client/2.0'
    __IDEMPOTENCY_HEADER_KEY = 'Idempotency-Key'
    __extra_headers = NullableDictType('__extra_headers')
    __extra_params = NullableDictType('__extra_params')
    __cookies = NullableDictType('__cookies')

    server_address = VeilUrlStringType('server_address')
    token = VeilJwtTokenType('token')

    def __init__(self, server_address: str, token: str, transfer_protocol: str, ssl_enabled: bool = True,
                 session_reopen: bool = False, timeout: int = 5 * 60, extra_headers: dict = None,
                 extra_params: dict = None, cookies: dict = None, json_serialize: aiohttp.client.JSONEncoder = None
                 ):
        """Please see help(VeilApiClient) for more info."""
        if aiohttp is None:
            raise RuntimeError('Please install `aiohttp`')  # pragma: no cover

        self.server_address = server_address
        self.token = token
        self.__session_reopen = session_reopen
        self.__ssl_enabled = ssl_enabled
        self.__transfer_protocol_prefix = transfer_protocol
        self.__extra_headers = extra_headers
        self.__extra_params = extra_params

        __timeout = aiohttp.ClientTimeout(total=timeout)
        __json_serialize = json_serialize
        self.__timeout = __timeout
        self.__cookies = cookies
        self.__json_serialize = __json_serialize

        self.__client_session = self.new_client_session

    async def __aenter__(self) -> 'VeilApiClient':
        """Async context manager enter."""
        return self

    async def __aexit__(self,
                        exc_type: Optional[Type[BaseException]],
                        exc_val: Optional[BaseException],
                        exc_tb: Optional[TracebackType]) -> None:
        """Async context manager exit."""
        await self.__session.close()

    async def close(self) -> None:
        """Session close."""
        await self.__session.close()

    @property
    def new_client_session(self):
        """Return new ClientSession instance."""
        return aiohttp.ClientSession(timeout=self.__timeout, cookies=self.__cookies,
                                     json_serialize=self.__json_serialize)

    @property
    def base_url(self):
        """Build controller api url."""
        return ''.join([self.__transfer_protocol_prefix, self.server_address, '/api/'])

    @property
    def __base_params(self) -> Dict:
        return {'async': 1}

    @property
    def __params(self) -> Dict:
        """Return base params extended by user extra params."""
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
        """Return base_headers extended by user extra_headers."""
        headers = self.__base_headers
        if self.__extra_headers and isinstance(self.__extra_headers, dict):
            headers.update(self.__extra_headers)
        return headers

    @property
    def __session(self) -> aiohttp.ClientSession:
        """Return connection ClientSession."""
        if self.__client_session.closed and self.__session_reopen:
            self.__client_session = self.new_client_session
        return self.__client_session

    async def __api_request(self, method_name: str, url: str, headers: dict, params: dict, ssl: bool,
                            json: dict = None) -> aiohttp.client_reqrep.ClientResponse:
        """Log parameters and execute passed aiohttp method."""
        # log request
        logger.debug('ssl: %s, url: %s, header: %s, params: %s, json: %s', self.__ssl_enabled, url, self.__headers,
                     params, json)
        # determine aiohttp.client method to call
        aiohttp_request_method = getattr(self.__session, method_name)
        # call aiohttp.client method
        return await aiohttp_request_method(url=url, headers=headers, params=params, ssl=ssl, json=json)

    @veil_api_response_decorator
    async def get(self, url, extra_params: dict = None) -> aiohttp.client_reqrep.ClientResponse:
        """Send GET request to VeiL ECP."""
        params = self.__params
        if extra_params:
            params.update(extra_params)
        return await self.__api_request('get', url,
                                        headers=self.__headers,
                                        params=params,
                                        ssl=self.__ssl_enabled)

    @veil_api_response_decorator
    async def post(self, url, json=None) -> aiohttp.client_reqrep.ClientResponse:
        """Send POST request to VeiL ECP."""
        return await self.__api_request('post', url,
                                        headers=self.__headers,
                                        params=self.__params,
                                        ssl=self.__ssl_enabled,
                                        json=json)

    @veil_api_response_decorator
    async def put(self, url, json=None) -> aiohttp.client_reqrep.ClientResponse:
        """Send PUT request to VeiL ECP."""
        return await self.__api_request('put', url,
                                        headers=self.__headers,
                                        params=self.__params,
                                        ssl=self.__ssl_enabled,
                                        json=json)
