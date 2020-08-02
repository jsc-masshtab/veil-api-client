# -*- coding: utf-8 -*-
"""Veil domain entity."""
from ..base.api_object import VeilApiObject, VeilRestPaginator
from ..base.api_response import VeilApiResponse
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
        cluster_id:  node_id: VeiL cluster id(uuid) for extra filtering.
        node_id:  node_id: VeiL node id(uuid) for extra filtering.
        data_pool_id:  node_id: VeiL data-pool id(uuid) for extra filtering.
        template:  VeiL template sign. Int because of ujson limitations (only str or int).
    """

    __API_OBJECT_PREFIX = 'domains/'

    def __init__(self, client, domain_id: str = None, cluster_id: str = None, node_id: str = None,
                 data_pool_id: str = None, template: int = None) -> None:
        """Please see help(VeilDomain) for more info.

        Arguments:
            template: Boolean int (0|1).
        """
        super().__init__(client, api_object_id=domain_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.remote_access = None
        self.verbose_name = None
        self.node = None
        self.parent = None
        self.remote_access_port = None
        self.graphics_password = None
        self.template = template
        # cluster_id, node_id or data_pool_id can be UUID.
        self.cluster_id = str(cluster_id) if cluster_id else None
        self.node_id = str(node_id) if node_id else None
        self.data_pool_id = str(data_pool_id) if data_pool_id else None

    def action_url(self, action: str) -> str:
        """Build domain action full url."""
        return self.api_object_url + action

    async def start(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'start'."""
        url = self.action_url('start/')
        body = dict(force=force)
        response = await self._client.post(url=url, json=body)
        return response

    async def reboot(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'reboot'."""
        url = self.action_url('reboot/')
        body = dict(force=force)
        response = await self._client.post(url=url, json=body)
        return response

    async def suspend(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'suspend'."""
        url = self.action_url('suspend/')
        body = dict(force=force)
        response = await self._client.post(url=url, json=body)
        return response

    async def reset(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'reset'."""
        url = self.action_url('reset/')
        body = dict(force=force)
        response = await self._client.post(url=url, json=body)
        return response

    async def shutdown(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'shutdown'."""
        url = self.action_url('shutdown/')
        body = dict(force=force)
        response = await self._client.post(url=url, json=body)
        return response

    async def resume(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'resume'."""
        url = self.action_url('resume/')
        body = dict(force=force)
        response = await self._client.post(url=url, json=body)
        return response

    async def remote_access_action(self, enable: bool = True) -> 'VeilApiResponse':
        """Send domain action 'remote-action'."""
        url = self.api_object_url + 'remote-access/'
        body = dict(remote_access=enable)
        response = await self._client.post(url, json=body)
        return response

    async def enable_remote_access(self) -> 'VeilApiResponse':
        """Enable domain remote-access."""
        return await self.remote_access_action(enable=True)

    async def disable_remote_access(self) -> 'VeilApiResponse':
        """Disable domain remote-access."""
        return await self.remote_access_action(enable=False)

    @argument_type_checker_decorator
    async def create(self, domain_configuration: DomainConfiguration) -> 'VeilApiResponse':
        """Run multi-create-domain on VeiL ECP."""
        url = self.base_url + 'multi-create-domain/'
        response = await self._client.post(url=url, json=domain_configuration.__dict__)
        return response

    async def remove(self, full: bool = True, force: bool = False) -> 'VeilApiResponse':
        """Remove domain instance on VeiL ECP."""
        url = self.api_object_url + 'remove/'
        body = dict(full=full, force=force)
        response = await self._client.post(url=url, json=body)
        return response

    async def list(self, with_vdisks: bool = True, paginator: 'VeilRestPaginator' = None) -> 'VeilApiResponse':  # noqa
        """Get list of data_pools with node_id filter.

        By default get only domains with vdisks.
        """
        # TODO: veil problems. temporary disabled
        # extra_params = dict(with_vdisks=int(with_vdisks))
        extra_params = dict()
        if self.cluster_id:
            extra_params['cluster'] = self.cluster_id
        if self.node_id:
            extra_params['node'] = self.node_id
        if self.data_pool_id:
            extra_params['datapool'] = self.data_pool_id
        if isinstance(self.template, int):
            extra_params['template'] = self.template
        elif isinstance(self.template, bool):
            # ujson can`t work with booleans
            extra_params['template'] = int(self.template)

        return await super().list(paginator=paginator, extra_params=extra_params)
