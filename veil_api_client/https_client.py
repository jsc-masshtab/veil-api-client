# -*- coding: utf-8 -*-
"""Veil https api client."""
from weakref import WeakValueDictionary

from .api_objects.cluster import VeilCluster
from .api_objects.controller import VeilController
from .api_objects.data_pool import VeilDataPool
from .api_objects.domain import VeilDomain
from .api_objects.node import VeilNode
from .api_objects.task import VeilTask
from .api_objects.vdisk import VeilVDisk
from .base.api_client import VeilApiClient

# TODO: протестировать не дублируются ли сессии на veil (с синглтоном и без).
# TODO: решить использовать ли синглтон и если использовать - какой


# def address_singleton(cls):
#     """Попытка предотвратить дублирование сессий."""
#     client_instances = dict()
#
#     def get_instance(*args, **kwargs):
#         server_address = args[0] if args else kwargs.get('server_address')
#
#         if server_address and server_address in client_instances:
#             return client_instances[server_address]
#         client_instances[server_address] = cls(*args, **kwargs)
#         return client_instances[server_address]
#     return get_instance


class Singleton(type):
    """Metaclass for VeilClient - singleton by server_address."""

    __client_instances = WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        server_address = args[0] if args else kwargs.get('server_address')

        if server_address and server_address in cls.__client_instances:
            return cls.__client_instances[server_address]

        instance = super().__call__(*args, **kwargs)
        cls.__client_instances[server_address] = instance
        return cls.__client_instances[server_address]


class VeilClient(VeilApiClient, metaclass=Singleton):
    __TRANSFER_PROTOCOL_PREFIX = 'https://'

    def __init__(self, server_address: str, token: str, ssl_enabled: bool = True, session_reopen: bool = False,
                 timeout: int = 5 * 60,
                 extra_headers: dict = None, extra_params: dict = None):
        super().__init__(server_address=server_address, token=token, transfer_protocol=self.__TRANSFER_PROTOCOL_PREFIX,
                         ssl_enabled=ssl_enabled,
                         session_reopen=session_reopen,
                         extra_headers=extra_headers,
                         extra_params=extra_params,
                         timeout=timeout)

    def domain(self, domain_id: str = None):
        return VeilDomain(client=self, domain_id=domain_id)

    def controller(self, controller_id: str = None):
        return VeilController(client=self, controller_id=controller_id)

    def cluster(self, cluster_id: str = None):
        return VeilCluster(client=self, cluster_id=cluster_id)

    def data_pool(self, data_pool_id: str = None):
        return VeilDataPool(client=self, data_pool_id=data_pool_id)

    def node(self, node_id: str = None):
        return VeilNode(client=self, node_id=node_id)

    def vdisk(self, vdisk_id: str = None):
        return VeilVDisk(client=self, vdisk_id=vdisk_id)

    def task(self, task_id: str = None):
        return VeilTask(client=self, task_id=task_id)
