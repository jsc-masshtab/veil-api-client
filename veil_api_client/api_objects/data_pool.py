# -*- coding: utf-8 -*-
"""Veil data-pool entity."""
from ..base.api_object import VeilApiObject, VeilRestPaginator


class VeilDataPool(VeilApiObject):
    """Veil data-pool entity.

    Attributes:
        client: https_client instance.
        data_pool_id: VeiL data-pool id(uuid) for extra filtering.
        node_id:  node_id: VeiL node id(uuid) for extra filtering.
    """

    __API_OBJECT_PREFIX = 'data-pools/'

    def __init__(self, client, data_pool_id: str = None, node_id: str = None) -> None:
        """Please see help(VeilDataPool) for more info."""
        super().__init__(client, api_object_id=data_pool_id, api_object_prefix=self.__API_OBJECT_PREFIX)
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

    async def list(self, paginator: VeilRestPaginator = None):  # noqa
        """Get list of data_pools with node_id filter."""
        extra_params = {'node': self.node_id} if self.node_id else None
        return await super().list(paginator=paginator, extra_params=extra_params)
