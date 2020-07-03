# -*- coding: utf-8 -*-
"""Veil domain entity."""
from ..base.api_object import VeilApiObject
from ..base.descriptors import BoolType, StringType, UuidStringType, argument_type_checker_decorator


class DomainConfiguration:
    """Simplified Veil domain description.

    Structure for VeiL domain copy.

    Attributes:
        verbose_name: domain verbose name.
        node: VeiL node id(uuid).
        datapool: VeiL data-pool id(uuid).
        parent: VeiL parent domain id(uuid).
        thin: created domain should be a thin clone of parent domain.
    """

    verbose_name = StringType('verbose_name')
    node = UuidStringType('node')
    datapool = UuidStringType('datapool')
    parent = UuidStringType('parent')
    thin = BoolType('thin')

    def __init__(self, verbose_name: str, node: str, datapool: str, parent: str, thin: bool = True) -> None:
        """Please see help(DomainConfiguration) for more info."""
        self.verbose_name = verbose_name
        self.node = node
        self.datapool = datapool
        self.parent = parent
        self.thin = thin


class VeilDomain(VeilApiObject):
    """Veil domain entity.

    Attributes:
        client: https_client instance.
        domain_id: VeiL domain id(uuid).
    """

    __API_OBJECT_PREFIX = 'domains/'

    def __init__(self, client, domain_id: str = None) -> None:
        """Please see help(VeilDomain) for more info."""
        super().__init__(client, api_object_id=domain_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.remote_access = None
        self.verbose_name = None
        self.node = None
        self.parent = None

    def action_url(self, action: str):
        """Build domain action full url."""
        return self.api_object_url + action + '/'

    async def start(self):
        """Send domain action 'start'."""
        url = self.action_url('start/')
        response = await self._client.post(url)
        return response

    async def reboot(self):
        """Send domain action 'reboot'."""
        url = self.action_url('reboot/')
        response = await self._client.post(url)
        return response

    async def suspend(self):
        """Send domain action 'suspend'."""
        url = self.action_url('suspend/')
        response = await self._client.post(url)
        return response

    async def reset(self):
        """Send domain action 'reset'."""
        url = self.action_url('reset/')
        response = await self._client.post(url)
        return response

    async def shutdown(self):
        """Send domain action 'shutdown'."""
        url = self.action_url('shutdown/')
        response = await self._client.post(url)
        return response

    async def resume(self):
        """Send domain action 'resume'."""
        url = self.action_url('resume/')
        response = await self._client.post(url)
        return response

    async def remote_access_action(self, enable: bool = True):
        """Send domain action 'remote-action'."""
        url = self.api_object_url + 'remote-access/'
        body = dict(remote_access=enable)
        response = await self._client.post(url, json=body)
        return response

    async def enable_remote_access(self):
        """Enable domain remote-access."""
        return await self.remote_access_action(enable=True)

    async def disable_remote_access(self):
        """Disable domain remote-access."""
        return await self.remote_access_action(enable=False)

    @argument_type_checker_decorator
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
