# -*- coding: utf-8 -*-
"""Veil node entity."""
from typing import Optional

try:
    from aiohttp.client_reqrep import ClientResponse
except ImportError:  # pragma: no cover
    ClientResponse = None

from ..base import (VeilApiObject, VeilCacheConfiguration,
                    VeilRestPaginator, VeilRetryConfiguration)


class VeilNode(VeilApiObject):
    """Veil node entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL node id(uuid).
        cluster_id: VeiL cluster id(uuid) for extra filtering.
    """

    __API_OBJECT_PREFIX = 'nodes/'

    def __init__(self, client,
                 api_object_id: Optional[str] = None,
                 cluster_id: Optional[str] = None,
                 resource_pool_id: Optional[str] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None) -> None:
        """Please see help(VeilNode) for more info."""
        super().__init__(client,
                         api_object_id=api_object_id,
                         api_object_prefix=self.__API_OBJECT_PREFIX,
                         retry_opts=retry_opts,
                         cache_opts=cache_opts)
        self.description = None
        self.locked_by = None
        self.created = None
        self.management_ip = None
        self.memory_count = None
        self.cpu_topology = None
        self.ipmi_ip = None
        self.ipmi_username = None
        self.cluster = None
        self.cluster_name = None
        self.version = None
        self.ballooning = None
        self.datacenter_name = None
        self.cpu_count = None
        # cluster_id can be UUID.
        self.cluster_id = str(cluster_id) if cluster_id else None
        self.resource_pool_id = str(resource_pool_id) if resource_pool_id else None

    async def usage(self) -> 'ClientResponse':
        """Get minimum resource load statistics on a node."""
        url = self.api_object_url + 'usage/'
        response = await self._get(url)
        return response

    async def list(self, paginator: Optional[VeilRestPaginator] = None) -> 'ClientResponse':  # noqa: A003,E501
        """Get list of nodes with cluster_id filter."""
        extra_cluster_param = {'cluster': self.cluster_id} if self.cluster_id else dict()
        extra_resource_pool_param = {'resource_pool': self.resource_pool_id} if self.resource_pool_id else dict()  # noqa: E501
        extra_params = dict()
        extra_params.update(extra_cluster_param)
        extra_params.update(extra_resource_pool_param)
        return await super().list(paginator=paginator, extra_params=extra_params)

    async def usb_devices(self):
        """Get list of usb devices."""
        url = self.api_object_url + 'usb-devices/'
        response = await self._get(url)
        return response
