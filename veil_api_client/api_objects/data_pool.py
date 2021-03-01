# -*- coding: utf-8 -*-
"""Veil data-pool entity."""
from typing import Optional

from ..base import (VeilApiObject, VeilApiResponse,
                    VeilCacheConfiguration, VeilRestPaginator, VeilRetryConfiguration)


class VeilDataPool(VeilApiObject):
    """Veil data-pool entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL data-pool id(uuid) for extra filtering.
        node_id:  node_id: VeiL node id(uuid) for extra filtering.
        cluster_id:  node_id: VeiL cluster id(uuid) for extra filtering.
    """

    __API_OBJECT_PREFIX = 'data-pools/'

    def __init__(self, client,
                 api_object_id: Optional[str] = None,
                 node_id: Optional[str] = None,
                 cluster_id: Optional[str] = None,
                 resource_pool_id: Optional[str] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None) -> None:
        """Please see help(VeilDataPool) for more info."""
        super().__init__(client,
                         api_object_id=api_object_id,
                         api_object_prefix=self.__API_OBJECT_PREFIX,
                         retry_opts=retry_opts,
                         cache_opts=cache_opts)
        self.description = None
        self.type = None
        self.used_space = None
        self.shared_storage = None
        self.size = None
        self.free_space = None
        self.created = None
        self.path = None
        # node_id can be UUID.
        self.node_id = str(node_id) if node_id else None
        self.cluster_id = str(cluster_id) if cluster_id else None
        self.resource_pool_id = str(resource_pool_id) if resource_pool_id else None

    async def list(self, paginator: Optional[VeilRestPaginator] = None) -> 'VeilApiResponse':  # noqa: A003, E501
        """Get list of data_pools with node_id filter."""
        extra_node_param = {'node': self.node_id} if self.node_id else dict()
        extra_cluster_param = {'cluster': self.cluster_id} if self.cluster_id else dict()
        extra_resource_pool_param = {'resource_pool': self.resource_pool_id} if self.resource_pool_id else dict()  # noqa: E501
        extra_params = dict()
        extra_params.update(extra_cluster_param)
        extra_params.update(extra_node_param)
        extra_params.update(extra_resource_pool_param)
        if not extra_params:
            extra_params = None
        return await super().list(paginator=paginator, extra_params=extra_params)
