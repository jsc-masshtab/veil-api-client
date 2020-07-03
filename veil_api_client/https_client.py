# -*- coding: utf-8 -*-
"""Veil https api client."""
import json
from weakref import WeakValueDictionary

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


class Singleton(type):
    """Metaclass for VeilClient - singleton by server_address."""

    __client_instances = WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        """Return VeilClient instance if it exists.

        If VeilClient with server_address already exists - no need to create new.
        If you need to destroy existing session - use del in your code.
        """
        server_address = args[0] if args else kwargs.get('server_address')

        if server_address and server_address in cls.__client_instances:
            return cls.__client_instances[server_address]

        instance = super().__call__(*args, **kwargs)
        cls.__client_instances[server_address] = instance
        return cls.__client_instances[server_address]


class VeilClient(VeilApiClient, metaclass=Singleton):
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

    def domain(self, domain_id: str = None):
        """Return VeilDomain entity."""
        return VeilDomain(client=self, domain_id=domain_id)

    def controller(self, controller_id: str = None):
        """Return VeilController entity."""
        return VeilController(client=self, controller_id=controller_id)

    def cluster(self, cluster_id: str = None):
        """Return VeilCluster entity."""
        return VeilCluster(client=self, cluster_id=cluster_id)

    def data_pool(self, data_pool_id: str = None):
        """Return VeilDataPool entity."""
        return VeilDataPool(client=self, data_pool_id=data_pool_id)

    def node(self, node_id: str = None):
        """Return VeilNode entity."""
        return VeilNode(client=self, node_id=node_id)

    def vdisk(self, vdisk_id: str = None):
        """Return VeilVDisk entity."""
        return VeilVDisk(client=self, vdisk_id=vdisk_id)

    def task(self, task_id: str = None):
        """Return VeilTask entity."""
        return VeilTask(client=self, task_id=task_id)
