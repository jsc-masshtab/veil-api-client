# -*- coding: utf-8 -*-
"""Veil resource-pool entity."""
from typing import Optional

from ..base import (VeilApiObject, VeilApiResponse,
                    VeilCacheConfiguration, VeilRestPaginator, VeilRetryConfiguration)


class VeilResourcePool(VeilApiObject):
    """Veil resource-pool entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL resource-pool id(uuid) for extra filtering.
        node_id:  node_id: VeiL node id(uuid) for extra filtering.
        cluster_id:  node_id: VeiL cluster id(uuid) for extra filtering.
    """

    __API_OBJECT_PREFIX = 'resource-pools/'

    def __init__(self, client,
                 api_object_id: Optional[str] = None,
                 node_id: Optional[str] = None,
                 cluster_id: Optional[str] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None) -> None:
        """Please see help(VeilResourcePool) for more info."""
        super().__init__(client,
                         api_object_id=api_object_id,
                         api_object_prefix=self.__API_OBJECT_PREFIX,
                         retry_opts=retry_opts,
                         cache_opts=cache_opts)
        self.hints = None
        self.tags = None
        self.domains_count = None
        self.cpu_limit = None
        self.memory_limit = None
        self.description = None

        self.cpu_shares = None
        self.memory_shares = None
        self.cpu_min_guarantee = None
        self.memory_min_guarantee = None
        self.cpu_limit = None
        self.memory_limit = None
        self.cpu_shares_actual = None
        self.memory_shares_actual = None
        self.nodes_cpu_count = None
        self.nodes_memory_count = None
        self.domains_cpu_count = None
        self.domains_memory_count = None
        self.domains_cpu_free = None
        self.domains_memory_free = None
        self.cpu_min_guarantee_per_domain = None
        self.memory_min_guarantee_per_domain = None
        self.cpu_min_guarantee_per_domain_actual = None
        self.memory_min_guarantee_per_domain_actual = None
        self.size_limit = None

        # node_id can be UUID.
        self.node_id = str(node_id) if node_id else None
        self.cluster_id = str(cluster_id) if cluster_id else None

    async def list(self, paginator: VeilRestPaginator = None) -> 'VeilApiResponse':  # noqa: A003, E501
        """Get list of resource-pools with filters."""
        extra_node_param = {'node': self.node_id} if self.node_id else dict()
        extra_cluster_param = {'cluster': self.cluster_id} if self.cluster_id else dict()
        extra_params = dict()
        extra_params.update(extra_cluster_param)
        extra_params.update(extra_node_param)
        if not extra_params:
            extra_params = None
        return await super().list(paginator=paginator, extra_params=extra_params)
