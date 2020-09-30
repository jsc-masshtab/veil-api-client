# -*- coding: utf-8 -*-
"""Veil api client."""
import asyncio
import logging
from types import TracebackType
from typing import Dict, Optional, Type
from uuid import uuid4

try:
    import aiohttp
except ImportError:  # pragma: no cover
    aiohttp = None

from .api_cache import cached_response_decorator
from .utils import (IntType, NullableDictType, NullableSetType, VeilJwtTokenType, VeilUrlStringType,
                    veil_api_response_decorator)

logger = logging.getLogger('veil-api-client.request')
logger.addHandler(logging.NullHandler())


class VeilRetryOptions:
    """Retry options class for veil api client.

    Attributes:
        num_of_attempts: num of retry attempts.
        timeout: base try timeout time (with exponential grow).
        max_timeout: max timeout between tries.
        timeout_increase_step: timeout increase step.
        status_codes: collection of response status codes witch must be repeated.
        exceptions: collection of aiohttp exceptions witch must be repeated.
    """

    num_of_attempts = IntType('num_of_attempts')
    timeout = IntType('timeout')
    max_timeout = IntType('max_timeout')
    timeout_increase_step = IntType('timeout_increase_step')
    status_codes = NullableSetType('status_codes')
    exceptions = NullableSetType('exceptions')

    def __init__(self,
                 num_of_attempts: int = 0,
                 timeout: int = 1,
                 max_timeout: int = 30,
                 timeout_increase_step: int = 2,
                 status_codes: set = None,
                 exceptions: set = None
                 ) -> None:
        """Please see help(VeilRetryOptions) for more info."""
        self.num_of_attempts = num_of_attempts
        self.timeout = timeout
        self.max_timeout = max_timeout
        self.timeout_increase_step = timeout_increase_step
        self.status_codes = status_codes
        self.exceptions = exceptions


class _RequestContext:
    """Custom aiohttp.RequestContext class for request retry logic.

    Attributes:
        request: aiohttp.request operation (POST, GET, etc).
        url: request url
        num_of_attempts: num of retry attempts if request failed.
        timeout: base try timeout time (with exponential grow).
        max_timeout: max timeout between tries.
        timeout_increase_step: timeout increase step.
        status_codes: collection of response status codes witch must be repeated.
        exceptions: collection of aiohttp exceptions witch must be repeated.
        kwargs: additional aiohttp.request arguments, such as headers and etc.
    """

    def __init__(self,
                 request: aiohttp.ClientRequest,
                 url: str,
                 num_of_attempts: int,
                 timeout: int,
                 max_timeout: int,
                 timeout_increase_step: int,
                 status_codes: set,
                 exceptions: set,
                 **kwargs
                 ) -> None:
        """Please see help(_RequestContext) for more info."""
        self._request = request
        self._url = url

        self._num_of_attempts = num_of_attempts
        self._timeout = timeout
        self._max_timeout = max_timeout
        self._timeout_increase_step = timeout_increase_step

        if status_codes is None:
            status_codes = set()
        self._status_codes = status_codes

        if exceptions is None:
            exceptions = set()
        self._exceptions = exceptions

        self._kwargs = kwargs

        self._current_attempt = 0
        self._response = None

    @property
    def _exp_timeout(self) -> float:
        """Retry request timeout witch can exponentially grow."""
        timeout = self._timeout * (self._timeout_increase_step ** (self._current_attempt - 1))
        return min(timeout, self._max_timeout)

    def _bad_code(self, code: int) -> bool:
        """Check that request status_code is bad."""
        return 500 <= code <= 599 or code in self._status_codes

    async def _execute_request(self) -> aiohttp.ClientResponse:
        """Run client request on aiohttp."""
        try:
            self._current_attempt += 1

            if self._current_attempt > 1:
                logger.debug('Request %s attempt', self._current_attempt)

            response = await self._request(self._url, **self._kwargs)
            code = response.status
            if self._current_attempt < self._num_of_attempts and self._bad_code(code):
                await asyncio.sleep(self._exp_timeout)
                return await self._execute_request()
            self._response = response
            return response
        except Exception as e:
            if self._current_attempt < self._num_of_attempts:
                for exc in self._exceptions:
                    if isinstance(e, exc):
                        await asyncio.sleep(self._exp_timeout)
                        return await self._execute_request()
            raise e

    async def __aenter__(self) -> aiohttp.ClientResponse:
        return await self._execute_request()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._response is not None:
            if not self._response.closed:
                self._response.close()


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
        retry_opts: VeilRetryOptions instance.
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
                 extra_params: dict = None, cookies: dict = None, json_serialize: aiohttp.client.JSONEncoder = None,
                 retry_opts: VeilRetryOptions = None
                 ) -> None:
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

        self.__retry_opts = retry_opts
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
    def new_client_session(self) -> 'aiohttp.ClientSession':
        """Return new ClientSession instance."""
        return aiohttp.ClientSession(timeout=self.__timeout, cookies=self.__cookies,
                                     json_serialize=self.__json_serialize)

    @property
    def base_url(self) -> str:
        """Build controller api url."""
        return ''.join([self.__transfer_protocol_prefix, self.server_address, '/api/'])

    @property
    def __base_params(self) -> Dict[str, int]:
        """All requests to VeiL should be async by default."""
        return {'async': 1}

    @property
    def __params(self) -> Dict:
        """Return base params extended by user extra params."""
        params = self.__base_params
        if self.__extra_params and isinstance(self.__extra_params, dict):
            params.update(self.__extra_params)
        return params

    @property
    def __base_headers(self) -> Dict[str, str]:
        """Return preconfigured request headers.

        Note:
            response should be json encoded on utf-8 and EN locale.
        """
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
    def __headers(self) -> Dict[str, str]:
        """Return base_headers extended by user extra_headers."""
        headers = self.__base_headers
        if self.__extra_headers and isinstance(self.__extra_headers, dict):
            headers.update(self.__extra_headers)
        return headers

    @property
    def __session(self) -> 'aiohttp.ClientSession':
        """Return connection ClientSession."""
        if self.__client_session.closed and self.__session_reopen:
            self.__client_session = self.new_client_session
        return self.__client_session

    def request_context(self, request: aiohttp.ClientRequest, url: str, headers: dict, params: dict, ssl: bool,
                        json: dict = None):
        """Create new _RequestContext instance."""
        return _RequestContext(request=request, url=url, headers=headers, params=params,
                               ssl=ssl, json=json,
                               num_of_attempts=self.__retry_opts.num_of_attempts,
                               timeout=self.__retry_opts.timeout,
                               max_timeout=self.__retry_opts.max_timeout,
                               timeout_increase_step=self.__retry_opts.timeout_increase_step,
                               status_codes=self.__retry_opts.status_codes,
                               exceptions=self.__retry_opts.exceptions)

    @staticmethod
    async def __fetch_response_data(response: aiohttp.ClientResponse) -> Dict[str, str]:
        """Collect all response attributes."""
        if isinstance(response, aiohttp.ClientResponse):
            # Collect response data
            async with response:
                status_code = response.status
                headers = response.headers
                data = await response.json()
            return dict(status_code=status_code, headers=dict(headers), data=data)

    async def __api_request(self, method_name: str, url: str, headers: dict, params: dict, ssl: bool,
                            json: dict = None) -> Dict[str, str]:
        """Log parameters and execute passed aiohttp method without retry."""
        print('simple request')
        # log request
        logger.debug('ssl: %s, url: %s, header: %s, params: %s, json: %s', self.__ssl_enabled, url, self.__headers,
                     params, json)
        # determine aiohttp.client method to call
        aiohttp_request_method = getattr(self.__session, method_name)
        # call aiohttp.client method
        aiohttp_response = await aiohttp_request_method(url=url, headers=headers, params=params, ssl=ssl, json=json)
        # fetch response data
        response_data = await self.__fetch_response_data(aiohttp_response)
        return response_data

    async def __api_retry_request(self, method_name: str, url: str, headers: dict, params: dict, ssl: bool,
                                  json: dict = None) -> Dict[str, str]:
        """Log parameters and execute passed aiohttp method with retry options."""
        print('retry_request')
        # log request
        logger.debug('ssl: %s, url: %s, header: %s, params: %s, json: %s', self.__ssl_enabled, url, self.__headers,
                     params, json)
        # determine aiohttp.client method to call
        aiohttp_request_method = getattr(self.__session, method_name)
        # create aiohttp.request witch can be retried.
        aiohttp_request = self.request_context(request=aiohttp_request_method, url=url, headers=headers, params=params,
                                               ssl=ssl, json=json)
        # execute request and fetch response data
        async with aiohttp_request as aiohttp_response:
            return await self.__fetch_response_data(aiohttp_response)

    @veil_api_response_decorator
    @cached_response_decorator
    async def get(self, api_object, url: str,
                  extra_params: dict = None) -> Dict[str, str]:
        """Send GET request to VeiL ECP."""
        params = self.__params
        if extra_params:
            params.update(extra_params)
        logger.debug('%s GET request.', api_object.__class__.__name__)
        # Check what type of request we should use
        if self.__retry_opts:
            return await self.__api_retry_request('get', url,
                                                  headers=self.__headers,
                                                  params=params,
                                                  ssl=self.__ssl_enabled)
        return await self.__api_request('get', url,
                                        headers=self.__headers,
                                        params=params,
                                        ssl=self.__ssl_enabled)

    @veil_api_response_decorator
    async def post(self, api_object, url: str, json: dict = None, extra_params: dict = None) -> Dict[str, str]:
        """Send POST request to VeiL ECP."""
        params = self.__params
        if extra_params:
            params.update(extra_params)
        logger.debug('%s POST request.', api_object.__class__.__name__)
        return await self.__api_request('post', url,
                                        headers=self.__headers,
                                        params=params,
                                        ssl=self.__ssl_enabled,
                                        json=json)

    @veil_api_response_decorator
    async def put(self, api_object, url: str, json: dict = None, extra_params: dict = None) -> Dict[str, str]:
        """Send PUT request to VeiL ECP."""
        params = self.__params
        if extra_params:
            params.update(extra_params)
        logger.debug('%s PUT request.', api_object.__class__.__name__)
        return await self.__api_request('put', url,
                                        headers=self.__headers,
                                        params=params,
                                        ssl=self.__ssl_enabled,
                                        json=json)
