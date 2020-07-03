# -*- coding: utf-8 -*-
"""Veil node entity."""
from ..base.api_object import VeilApiObject


class VeilNode(VeilApiObject):
    """Veil node entity.

    Attributes:
        client: https_client instance.
        node_id: VeiL node id(uuid).
    """

    __API_OBJECT_PREFIX = 'nodes/'

    def __init__(self, client, node_id: str = None) -> None:
        """Please see help(VeilNode) for more info."""
        super().__init__(client, api_object_id=node_id, api_object_prefix=self.__API_OBJECT_PREFIX)
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

    async def usage(self):
        """Get minimum resource load statistics on a node."""
        url = self.api_object_url + 'usage/'
        response = await self._client.get(url)
        return response
