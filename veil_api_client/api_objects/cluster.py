# -*- coding: utf-8 -*-
"""Veil cluster entity."""
from ..base.api_object import VeilApiObject
from ..base.api_response import VeilApiResponse


class VeilCluster(VeilApiObject):
    """Veil cluster entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL cluster id(uuid).
    """

    __API_OBJECT_PREFIX = 'clusters/'

    def __init__(self, client, api_object_id: str = None) -> None:
        """Please see help(VeilCluster) for more info."""
        super().__init__(client, api_object_id=api_object_id, api_object_prefix=self.__API_OBJECT_PREFIX)
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
