# -*- coding: utf-8 -*-
"""Veil cluster entity."""
from typing import Optional

from ..base import (VeilApiObject, VeilApiResponse,
                    VeilCacheConfiguration, VeilRetryConfiguration)


class VeilCluster(VeilApiObject):
    """Veil cluster entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL cluster id(uuid).
    """

    __API_OBJECT_PREFIX = 'clusters/'

    def __init__(self, client,
                 api_object_id: Optional[str] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None) -> None:
        """Please see help(VeilCluster) for more info."""
        super().__init__(client,
                         api_object_id=api_object_id,
                         api_object_prefix=self.__API_OBJECT_PREFIX,
                         retry_opts=retry_opts,
                         cache_opts=cache_opts)
        self.cpu_count = None
        self.created = None
        self.description = None
        self.memory_count = None
        self.vdi = None
        self.nodes_count = None

    async def usage(self) -> 'VeilApiResponse':
        """Get minimum statistics of resource loading."""
        url = self.api_object_url + 'usage/'
        response = await self._get(url)
        return response
