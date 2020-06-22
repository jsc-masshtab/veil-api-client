# -*- coding: utf-8 -*-
"""Veil Task entity."""
from ..base.api_object import VeilApiObject


class VeilTask(VeilApiObject):
    __API_OBJECT_PREFIX = 'tasks/'

    def __init__(self, client, task_id: str = None):
        super().__init__(client, api_object_id=task_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.is_cancellable = None
        self.is_multitask = None
        self.progress = None
        self.error_message = None
        self.executed = None
        self.created = None
        self.name = None
        self.detail_message = None
        self.entities = None

    async def check(self):
        """Эндпоинт проверки завершённости задач."""
        url = self.base_url + 'check/'
        response = await self._client.put(url)
        return response

    async def count(self):
        """Эндпоинт счётчиков задач."""
        url = self.base_url + 'count/'
        response = await self._client.get(url)
        return response

    async def cancel(self):
        """Эндпоинт выхода из задач."""
        url = self.api_object_url + 'cancel/'
        response = await self._client.put(url)
        return response

    async def jid(self):
        """Эндоинт получения jid отдельной задачи."""
        url = self.api_object_url + 'jid/'
        response = await self._client.get(url)
        return response

    async def release_locks(self):
        """Эндпоинт сброса блокировок из задач."""
        url = self.api_object_url + 'release-locks/'
        response = await self._client.put(url)
        return response

    async def response(self):
        """Эндпоинт получения ответа от узла."""
        url = self.api_object_url + 'response/'
        response = await self._client.get(url)
        return response
