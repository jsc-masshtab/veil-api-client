# -*- coding: utf-8 -*-
"""Veil api cache drivers."""
import functools
import json
import logging
from enum import Enum

try:
    # TODO: заменить на Client из best practices
    from pymemcache.client.base import Client as MemcachedClient
except ImportError:  # pragma: no cover
    MemcachedClient = None

from .api_client import VeilApiClient
from .api_response import VeilApiResponse
from .descriptors import IntType


logger = logging.getLogger('veil-api-client.request')
logger.addHandler(logging.NullHandler())


class CacheType(Enum):
    """Supported caching types.

    name is python client library
    value is str representation
    """

    MemcachedClient = 'memcached'

    def __str__(self):
        """Representation of cache client library."""
        return self.value

    @property
    def client(self):
        """Enum name must be cache client class."""
        return eval(self.name)


class VeilCacheOptions:
    """VeilApiClient cache options.

    Arguments:
        cache_type: supported cache storage type (now only memcached).
        ttl - cache value time to live (int).
    """

    ttl = IntType

    def __init__(self, cache_type: CacheType, server: tuple, ttl: int) -> None:
        """Please see help(VeilCacheOptions) for more info."""
        self.cache_type = CacheType(cache_type)
        self.server = server
        self.ttl = ttl


# memcached client
class DictSerde:
    """Veil api response serializer for memcached."""

    @staticmethod
    def serialize(key, value):
        """Serialize VeilApiResponse to bytes."""
        if isinstance(value, str):
            return value.encode('utf-8'), 1
        elif isinstance(value, VeilApiResponse):
            response_data = {'data': value.data, 'status_code': value.status_code,
                             'headers': dict(value.headers),
                             }
            return json.dumps(response_data).encode('utf-8'), 3
        return json.dumps(value).encode('utf-8'), 2

    @staticmethod
    def deserialize(key, value, flags):
        """Deserialize bytes to VeilApiResponse."""
        if flags == 1:
            return value.decode('utf-8')
        elif flags == 2:
            return json.loads(value.decode('utf-8'))
        elif flags == 3:
            response_data = json.loads(value.decode('utf-8'))
            return VeilApiResponse(status_code=response_data['status_code'], data=response_data['data'],
                                   headers=response_data['headers'])
        raise Exception('Unknown serialization format')


def cached_response_decorator(func):
    """Check url and parameters in cache."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # TODO: функции set и get нужно вынести выше, чтобы можно было переопределить
        # TODO: класс клиента принимающий в конструктор класс из библиотеки и содержащий методы set и get,
        #  которые делают super() нужно класса
        # TODO: время жизни в параметрах клиента
        # TODO: use PooledClient
        # TODO: best practices from https://pymemcache.readthedocs.io/en/latest/getting_started.html

        # print('args:', args)
        # print('kwargs:', kwargs)
        # print('args:', args)
        # print(args[0]._cache_opts)
        # TODO: проверить через синглтон клиент

        # first element in args must be VeilClient instance
        if not args or not isinstance(args[0], VeilApiClient):
            return await func(*args, **kwargs)

        cache_opts = args[0]._cache_opts  # noqa
        # cache options must be set
        if not cache_opts:
            return await func(*args, **kwargs)
        # get client lib instance
        client = cache_opts.cache_type.client(cache_opts.server, serde=DictSerde())

        # arguments order is fixed
        url = kwargs['url'] if kwargs.get('url') else args[1]
        params = kwargs['extra_params'] if kwargs.get('extra_params') else args[2]

        cache_key = '{}|{}'.format(url, params)
        # cache key can`t contain spaces
        cache_key = cache_key.replace(' ', '')

        result = client.get(cache_key)
        if not result:
            result = await func(*args, **kwargs)
            # TODO: более явно перечислить статусы успеха на veil
            if result.status_code in (200, 201, 202, 204):
                # save request response to cache
                client.set(cache_key, result, expire=cache_opts.ttl)
        else:
            logger.debug('get %s response from cache', url)
        return result
    return wrapper
