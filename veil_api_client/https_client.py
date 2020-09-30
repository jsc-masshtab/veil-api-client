# -*- coding: utf-8 -*-
"""Veil https api client."""
import json

try:
    import ujson
except ImportError:  # pragma: no cover
    ujson = None

try:
    import pymemcache
except ImportError:  # pragma: no cover
    pymemcache = None

from .api_objects.cluster import VeilCluster
from .api_objects.controller import VeilController
from .api_objects.data_pool import VeilDataPool
from .api_objects.domain import VeilDomain
from .api_objects.node import VeilNode
from .api_objects.vdisk import VeilVDisk
from .base.api_cache import VeilCacheOptions
from .base.api_client import VeilApiClient, VeilRetryOptions
from .base.api_object import VeilTask
from .base.utils import IntType


class VeilClient(VeilApiClient):
    """Use this instead of VeilApiClient.

    Attributes:
        server_address: VeiL server address (without protocol)
        token: VeiL auth token.
        ssl_enabled: ssl-certificate validation.
        session_reopen: auto reopen aiohttp.ClientSession when it`s closed
        timeout: aiohttp.ClientSession total timeout.
        extra_headers: additional user headers.
        extra_params: additional user params.
        cookies: additional user cookies (probably useless)
        ujson_: ujson using.
    """

    __TRANSFER_PROTOCOL_PREFIX = 'https://'

    def __init__(self, server_address: str, token: str, ssl_enabled: bool = True, session_reopen: bool = False,
                 timeout: int = 5 * 60,
                 extra_headers: dict = None, extra_params: dict = None, cookies: dict = None,
                 ujson_: bool = True, cache_opts: VeilCacheOptions = None, retry_opts: VeilRetryOptions = None) -> None:
        """Please see help(VeilClient) for more info."""
        if ujson is None and ujson_:
            raise RuntimeError('Please install `ujson`')  # pragma: no cover
        if pymemcache is None and cache_opts:
            # TODO: чтобы была возможность использовать другие кеши - нужно изменить условие на более обтекаемое
            raise RuntimeError('For using cache please install `pymemcache`')  # pragma: no cover

        # ujson is much faster but less compatible
        serializer = ujson.dumps if ujson_ else json.dumps
        # cache options that can be used in request caching decorator
        self._cache_opts = cache_opts
        super().__init__(server_address=server_address, token=token, transfer_protocol=self.__TRANSFER_PROTOCOL_PREFIX,
                         ssl_enabled=ssl_enabled,
                         session_reopen=session_reopen,
                         extra_headers=extra_headers,
                         extra_params=extra_params,
                         timeout=timeout,
                         cookies=cookies,
                         json_serialize=serializer,
                         retry_opts=retry_opts)

    def domain(self, domain_id: str = None, cluster_id: str = None, node_id: str = None, data_pool_id: str = None,
               template: bool = None) -> 'VeilDomain':
        """Return VeilDomain entity."""
        return VeilDomain(client=self, template=template, api_object_id=domain_id, cluster_id=cluster_id,
                          node_id=node_id,
                          data_pool_id=data_pool_id)

    def controller(self, controller_id: str = None) -> 'VeilController':
        """Return VeilController entity."""
        return VeilController(client=self, api_object_id=controller_id)

    def cluster(self, cluster_id: str = None) -> 'VeilCluster':
        """Return VeilCluster entity."""
        return VeilCluster(client=self, api_object_id=cluster_id)

    def data_pool(self, data_pool_id: str = None, node_id: str = None, cluster_id: str = None) -> 'VeilDataPool':
        """Return VeilDataPool entity."""
        return VeilDataPool(client=self, api_object_id=data_pool_id, node_id=node_id, cluster_id=cluster_id)

    def node(self, node_id: str = None, cluster_id: str = None) -> 'VeilNode':
        """Return VeilNode entity."""
        return VeilNode(client=self, api_object_id=node_id, cluster_id=cluster_id)

    def vdisk(self, vdisk_id: str = None) -> 'VeilVDisk':
        """Return VeilVDisk entity."""
        return VeilVDisk(client=self, api_object_id=vdisk_id)

    def task(self, task_id: str = None) -> 'VeilTask':
        """Return VeilTask entity."""
        return VeilTask(client=self, api_object_id=task_id)


class VeilClientSingleton:
    """Contains previously initialized clients to minimize sessions on the VeiL controller.

    If you have always running application, such as Tornado web-server and you need to
    persistent VeiL ECP connections.
    """

    __client_instances = dict()
    __TIMEOUT = IntType('__TIMEOUT')

    def __init__(self, timeout: int = 5 * 60, cache_opts: VeilCacheOptions = None,
                 retry_opts: VeilRetryOptions = None) -> None:
        """Please see help(VeilClientSingleton) for more info."""
        self.__TIMEOUT = timeout
        self.__CACHE_OPTS = cache_opts
        self.__RETRY_OPTS = retry_opts

    def add_client(self, server_address: str, token: str,
                   timeout: int = None, cache_opts: VeilCacheOptions = None,
                   retry_opts: VeilRetryOptions = None) -> 'VeilClient':
        """Create new instance of VeilClient if it is not initialized on same address.

        Attributes:
            server_address: VeiL server address (without protocol).
            token: VeiL auth token.
            timeout: aiohttp.ClientSession total timeout.
        """
        _timeout = timeout if timeout else self.__TIMEOUT
        _cache_opts = cache_opts if cache_opts else self.__CACHE_OPTS
        _retry_opts = retry_opts if retry_opts else self.__RETRY_OPTS
        if server_address not in self.__client_instances:
            instance = VeilClient(server_address=server_address, token=token,
                                  session_reopen=True, timeout=_timeout, ujson_=True, cache_opts=_cache_opts,
                                  retry_opts=_retry_opts)
            self.__client_instances[server_address] = instance
        return self.__client_instances[server_address]

    async def remove_client(self, server_address: str) -> None:
        """Remove and close existing VeilClient instance."""
        if server_address in self.__client_instances:
            _client = self.__client_instances.pop(server_address)
            await _client.close()

    @property
    def instances(self) -> dict:
        """Show all instances of VeilClient."""
        return self.__client_instances
