# -*- coding: utf-8 -*-
"""Veil api cache drivers."""
import functools
import logging
from abc import ABCMeta, abstractmethod
from asyncio import iscoroutinefunction
from typing import Optional

from .utils import IntType, VeilConfiguration, VeilRetryConfiguration

logger = logging.getLogger('veil-api-client.request')
logger.addHandler(logging.NullHandler())


class VeilCacheAbstractClient(metaclass=ABCMeta):
    """User cache client Abstract class."""

    @abstractmethod
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
        """Abstract method for VeiLClient."""
        pass  # pragma: no cover


class VeilCacheConfiguration(VeilConfiguration):
    """VeilApiClient cache options.

    Arguments:
        cache_client: user custom cache class that can write and
            read request data from itself.
        ttl: cache value time to live (int).
    """

    ttl = IntType

    def __init__(self, cache_client: VeilCacheAbstractClient, ttl: int) -> None:
        """Please see help(VeilCacheConfiguration) for more info."""
        if cache_client and not isinstance(cache_client, VeilCacheAbstractClient):
            raise TypeError('cache_client must be VeilCacheAbstractClient descendant.')
        self.cache_client = cache_client
        self.ttl = ttl

    async def get_from_cache(self,
                             coroutine_function,
                             client,
                             method_name: str,
                             url: str,
                             headers: dict,
                             params: dict,
                             ssl: bool,
                             json_data: Optional[dict] = None,
                             retry_opts: Optional[VeilRetryConfiguration] = None,
                             *args, **kwargs):
        """Get response from a cache."""
        if self.cache_client and self.ttl > 0:
            return await self.cache_client.get_from_cache(coroutine_function,
                                                          client,
                                                          method_name,
                                                          url,
                                                          headers,
                                                          params,
                                                          ssl,
                                                          json_data,
                                                          retry_opts,
                                                          ttl=self.ttl,
                                                          *args, **kwargs)
        # If cache_opts are defined as no cache - just wait for a coroutine result.
        if iscoroutinefunction(coroutine_function):
            return await coroutine_function(client,
                                            method_name,
                                            url,
                                            headers,
                                            params,
                                            ssl,
                                            json_data,
                                            retry_opts,
                                            *args, **kwargs)
        raise NotImplementedError('coroutine_function should be a coroutine function.')


def cached_response(func):
    """Cache VeilApiResponse if cache_opts are properly determined."""

    @functools.wraps(func)
    async def wrapper(client,
                      method_name: str,
                      url: str,
                      headers: dict,
                      params: dict,
                      ssl: bool,
                      json_data: Optional[dict] = None,
                      retry_opts: Optional[VeilRetryConfiguration] = None,
                      cache_opts: Optional[VeilCacheConfiguration] = None,
                      *args, **kwargs):
        """cache_opts must be a VeilCacheConfiguration instance."""
        if cache_opts and isinstance(cache_opts, VeilCacheConfiguration):
            return await cache_opts.get_from_cache(func,
                                                   client,
                                                   method_name,
                                                   url,
                                                   headers,
                                                   params,
                                                   ssl,
                                                   json_data,
                                                   retry_opts,
                                                   *args, **kwargs)

        # If there is no proper cache configuration.
        return await func(client,
                          method_name=method_name,
                          url=url,
                          headers=headers,
                          params=params,
                          ssl=ssl,
                          json_data=json_data,
                          retry_opts=retry_opts,
                          *args, **kwargs)

    return wrapper
