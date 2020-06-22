# -*- coding: utf-8 -*-
"""Veil cluster entity."""
from ..base.api_object import VeilApiObject


class VeilCluster(VeilApiObject):
    __API_OBJECT_PREFIX = 'clusters/'

    def __init__(self, client, cluster_id: str = None):
        super().__init__(client, api_object_id=cluster_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.cpu_count = None
        self.created = None
        self.description = None
        self.memory_count = None
        self.vdi = None

    async def usage(self):
        """Получение минимальной статистики загрузки ресурсов."""
        url = self.api_object_url + 'usage/'
        response = await self._client.get(url)
        return response
