# -*- coding: utf-8 -*-
"""Veil domain entity."""
from ..base.api_object import VeilApiObject
from ..base.utils import BoolType, StringType, UuidStringType


class VeilDomain(VeilApiObject):
    __API_OBJECT_PREFIX = 'domains/'

    class DomainConfiguration:
        """Сокращенное описание структуры VeilDomain."""

        verbose_name = StringType('verbose_name')
        node = UuidStringType('node')
        datapool = UuidStringType('datapool')
        parent = UuidStringType('parent')
        thin = BoolType('thin')

        def __init__(self, verbose_name: str, node: str, datapool: str, parent: str, thin: bool = True):
            """На данный момент создание VM без указания родителя - запрещено."""
            self.verbose_name = verbose_name
            self.node = node
            self.datapool = datapool
            self.parent = parent
            self.thin = thin

    def __init__(self, client, domain_id: str = None):
        super().__init__(client, api_object_id=domain_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.remote_access = None
        self.verbose_name = None
        self.node = None
        self.parent = None

    def action_url(self, action: str):
        return self.api_object_url + action + '/'

    async def start(self):
        url = self.action_url('start/')
        response = await self._client.post(url)
        return response

    async def reboot(self):
        url = self.action_url('reboot/')
        response = await self._client.post(url)
        return response

    async def suspend(self):
        url = self.action_url('suspend/')
        response = await self._client.post(url)
        return response

    async def reset(self):
        url = self.action_url('reset/')
        response = await self._client.post(url)
        return response

    async def shutdown(self):
        url = self.action_url('shutdown/')
        response = await self._client.post(url)
        return response

    async def resume(self):
        url = self.action_url('resume/')
        response = await self._client.post(url)
        return response

    async def remote_access_action(self, enable: bool = True):
        url = self.api_object_url + 'remote-access/'
        body = dict(remote_access=enable)
        response = await self._client.post(url, json=body)
        return response

    async def enable_remote_access(self):
        return await self.remote_access_action(enable=True)

    async def disable_remote_access(self):
        return await self.remote_access_action(enable=False)

    async def create(self, domain_configuration: DomainConfiguration):
        """Run multi-create-domain on VeiL ECP."""
        url = self.base_url + 'multi-create-domain/'
        response = await self._client.post(url=url, json=domain_configuration.__dict__)
        return response

    async def remove(self, full: bool = True, force: bool = False):
        """Remove domain instance on VeiL ECP."""
        url = self.api_object_url + 'remove/'
        body = dict(full=full, force=force)
        response = await self._client.post(url=url, json=body)
        return response
