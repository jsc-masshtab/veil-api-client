# -*- coding: utf-8 -*-
"""Veil https api client."""
import json

try:
    import ujson
except ImportError:  # pragma: no cover
    ujson = None

from .api_objects.cluster import VeilCluster
from .api_objects.controller import VeilController
from .api_objects.data_pool import VeilDataPool
from .api_objects.domain import VeilDomain
from .api_objects.node import VeilNode
from .api_objects.task import VeilTask
from .api_objects.vdisk import VeilVDisk
from .base.api_client import VeilApiClient
from .base.descriptors import IntType


class VeilClient(VeilApiClient):
    """Use this instead of VeilApiClient."""

    __TRANSFER_PROTOCOL_PREFIX = 'https://'

    def __init__(self, server_address: str, token: str, ssl_enabled: bool = True, session_reopen: bool = False,
                 timeout: int = 5 * 60,
                 extra_headers: dict = None, extra_params: dict = None, cookies: dict = None,
                 ujson_: bool = True) -> None:
        """Please see help(VeilClient) for more info."""
        if ujson is None:
            raise RuntimeError('Please install `ujson`')  # pragma: no cover
        # ujson is much faster but less compatible
        serializer = ujson.dumps if ujson_ else json.dumps
        super().__init__(server_address=server_address, token=token, transfer_protocol=self.__TRANSFER_PROTOCOL_PREFIX,
                         ssl_enabled=ssl_enabled,
                         session_reopen=session_reopen,
                         extra_headers=extra_headers,
                         extra_params=extra_params,
                         timeout=timeout,
                         cookies=cookies,
                         json_serialize=serializer)

    def domain(self, domain_id: str = None, cluster_id: str = None, node_id: str = None, data_pool_id: str = None,
               template: bool = None):
        """Return VeilDomain entity."""
        return VeilDomain(client=self, template=template, domain_id=domain_id, cluster_id=cluster_id, node_id=node_id,
                          data_pool_id=data_pool_id)

    def controller(self, controller_id: str = None):
        """Return VeilController entity."""
        return VeilController(client=self, controller_id=controller_id)

    def cluster(self, cluster_id: str = None):
        """Return VeilCluster entity."""
        return VeilCluster(client=self, cluster_id=cluster_id)

    def data_pool(self, data_pool_id: str = None, node_id: str = None):
        """Return VeilDataPool entity."""
        return VeilDataPool(client=self, data_pool_id=data_pool_id, node_id=node_id)

    def node(self, node_id: str = None, cluster_id: str = None):
        """Return VeilNode entity."""
        return VeilNode(client=self, node_id=node_id, cluster_id=cluster_id)

    def vdisk(self, vdisk_id: str = None):
        """Return VeilVDisk entity."""
        return VeilVDisk(client=self, vdisk_id=vdisk_id)

    def task(self, task_id: str = None):
        """Return VeilTask entity."""
        return VeilTask(client=self, task_id=task_id)


class VeilClientSingleton:
    """Contains previously initialized clients to minimize sessions on the VeiL controller.

    If you have always running application, such as Tornado web-server and you need to
    persistent VeiL ECP connections.
    """

    __client_instances = dict()
    __TIMEOUT = IntType('__TIMEOUT')

    def __init__(self, timeout: int = 5 * 60):
        """Please see help(VeilClientSingleton) for more info."""
        self.__TIMEOUT = timeout

    def add_client(self, server_address: str, token: str,
                   timeout: int = None):
        """Create new instance of VeilClient if it is not initialized on same address.

        Attributes:
            server_address: VeiL server address (without protocol).
            token: VeiL auth token.
            timeout: aiohttp.ClientSession total timeout.
        """
        _timeout = timeout if timeout else self.__TIMEOUT
        if server_address not in self.__client_instances:
            instance = VeilClient(server_address=server_address, token=token,
                                  session_reopen=True, timeout=_timeout, ujson_=True)
            self.__client_instances[server_address] = instance
        return self.__client_instances[server_address]

    async def remove_client(self, server_address: str):
        """Remove and close existing VeilClient instance."""
        if server_address in self.__client_instances:
            _client = self.__client_instances.pop(server_address)
            await _client.close()

    @property
    def instances(self) -> dict:
        """Show all instances of VeilClient."""
        return self.__client_instances
