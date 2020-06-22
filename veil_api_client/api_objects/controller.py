# -*- coding: utf-8 -*-
"""Veil controller entity."""
from ..base.api_object import VeilApiObject


class VeilController(VeilApiObject):
    __API_OBJECT_PREFIX = 'controllers/'

    def __init__(self, client, controller_id: str = None):
        super().__init__(client, api_object_id=controller_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.version = None

    async def base_version(self):
        """Получаем версию контроллера."""
        url = self.base_url + 'base-version/'
        response = await self._client.get(url)
        self.version = response.data.get('version')
        return response

    async def check(self):
        """Проверяем доступность контроллера."""
        url = self.base_url + 'check/'
        response = await self._client.get(url)
        return response

    @property
    async def ok(self):
        """Проверка доступности прошла успешно."""
        check_response = await self.check()
        return check_response.status_code == 200

    @property
    async def system_time(self) -> dict:
        """Получение текущего времени контроллера."""
        url = self.base_url + 'system-time/'
        time_response = await self._client.get(url)
        if time_response.status_code == 200:
            return time_response.data
