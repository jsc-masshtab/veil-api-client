# -*- coding: utf-8 -*-
"""Veil domain entity."""

from enum import Enum, IntEnum

from ..base.api_object import VeilApiObject, VeilRestPaginator
from ..base.api_response import VeilApiResponse
from ..base.utils import BoolType, StringType, UuidStringType, argument_type_checker_decorator


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


class MultiManagerAction(Enum):
    """Possible options for VeiL multi-manager."""

    START = 'start'
    SHUTDOWN = 'shutdown'
    SUSPEND = 'suspend'
    REBOOT = 'reboot'
    RESUME = 'resume'
    DELETE = 'delete'
    MIGRATE = 'migrate'


class DomainPowerState(IntEnum):
    """Veil domain power states."""

    UNDEFINED = 0
    OFF = 1
    SUSPENDED = 2
    ON = 3


class VeilGuestAgentCmd(Enum):
    """Veil guest agent commands."""

    LOCK_SCREEN = 'lock_screen'
    LOGOFF = 'logoff'
    SHUTDOWN = 'shutdown'
    LOGIN = 'login'
    HIBERNATE = 'hibernate'
    SET_NUMBER_OF_CPUS = 'set_number_of_cpus'
    ECHO = 'echo'
    LIFECYCLE_EVENT = 'lifecycle_event'
    MEMORY_STATS = 'memory_stats'
    DISK_USAGES = 'disk_usages'
    FREE_RAM = 'free_ram'
    API_VERSION = 'api_version'
    FQDN = 'fqdn'
    USER_INFO = 'user_info'
    TIMEZONE = 'timezone'
    INFO = 'info'
    OS_INFO = 'os_info'
    APP_LIST = 'app_list'


class DomainGuestUtils:

    def __init__(self, veil_state: bool = False, qemu_state: bool = False, version: str = None, hostname: str = None,
                 ipv4: list = None) -> None:
        self.veil_state = veil_state
        self.qemu_state = qemu_state
        self.version = version
        self.hostname = hostname
        self.ipv4 = ipv4

    @property
    def first_ipv4_ip(self):
        """First ipv4 address in list."""
        if not isinstance(self.ipv4, list):
            return None
        if len(self.ipv4) > 0:
            return self.ipv4[0]


class VeilDomain(VeilApiObject):
    """Veil domain entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL domain id(uuid).
        cluster_id:  node_id: VeiL cluster id(uuid) for extra filtering.
        node_id:  node_id: VeiL node id(uuid) for extra filtering.
        data_pool_id:  node_id: VeiL data-pool id(uuid) for extra filtering.
        template:  VeiL template sign. Int because of ujson limitations (only str or int).
    """

    __API_OBJECT_PREFIX = 'domains/'

    def __init__(self, client, api_object_id: str = None, cluster_id: str = None, node_id: str = None,
                 data_pool_id: str = None, template: int = None) -> None:
        """Please see help(VeilDomain) for more info.

        Arguments:
            template: Boolean int (0|1).
        """
        super().__init__(client, api_object_id=api_object_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.remote_access = None
        self.verbose_name = None
        self.node = None
        self.parent = None
        self.remote_access_port = None
        self.graphics_password = None
        self.template = template
        self.os_type = None
        self.user_power_state = 0
        self.guest_utils = None
        # cluster_id, node_id or data_pool_id can be UUID.
        self.cluster_id = str(cluster_id) if cluster_id else None
        self.node_id = str(node_id) if node_id else None
        self.data_pool_id = str(data_pool_id) if data_pool_id else None

    @property
    def guest_agent(self):
        """Verbose domain guest utils."""
        return DomainGuestUtils(**self.guest_utils)

    @property
    def power_state(self):
        """Verbose domain power state."""
        return DomainPowerState(self.user_power_state)

    def action_url(self, action: str) -> str:
        """Build domain action full url."""
        return self.api_object_url + action

    @argument_type_checker_decorator
    async def guest_command(self, veil_cmd: VeilGuestAgentCmd = None, qemu_cmd: str = None, fargs: dict = None,
                            timeout: int = 5):
        """Guest agent commands endpoint."""
        url = self.api_object_url + 'guest-command/'
        body = dict()
        if veil_cmd:
            body['veil_cmd'] = veil_cmd.value
        if qemu_cmd:
            body['qemu_cmd'] = qemu_cmd
        if fargs:
            body['fargs'] = fargs
        if timeout:
            body['timeout'] = timeout
        response = await self._post(url=url, json=body)
        return response

    async def set_hostname(self, hostname: str = None):
        """Set domain hostname on VeiL ECP."""
        url = self.api_object_url + 'set-hostname/'
        domain_hostname = hostname if hostname else self.verbose_name
        body = dict(hostname=domain_hostname)
        response = await self._post(url=url, json=body)
        return response

    async def start(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'start'."""
        url = self.action_url('start/')
        body = dict(force=force)
        response = await self._post(url=url, json=body)
        return response

    async def reboot(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'reboot'."""
        url = self.action_url('reboot/')
        body = dict(force=force)
        response = await self._post(url=url, json=body)
        return response

    async def suspend(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'suspend'."""
        url = self.action_url('suspend/')
        body = dict(force=force)
        response = await self._post(url=url, json=body)
        return response

    async def reset(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'reset'."""
        url = self.action_url('reset/')
        body = dict(force=force)
        response = await self._post(url=url, json=body)
        return response

    async def shutdown(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'shutdown'."""
        url = self.action_url('shutdown/')
        body = dict(force=force)
        response = await self._post(url=url, json=body)
        return response

    async def resume(self, force: bool = False) -> 'VeilApiResponse':
        """Send domain action 'resume'."""
        url = self.action_url('resume/')
        body = dict(force=force)
        response = await self._post(url=url, json=body)
        return response

    async def remote_access_action(self, enable: bool = True) -> 'VeilApiResponse':
        """Send domain action 'remote-action'."""
        url = self.api_object_url + 'remote-access/'
        body = dict(remote_access=enable)
        response = await self._post(url, json=body)
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
        response = await self._post(url=url, json=domain_configuration.__dict__)
        return response

    async def remove(self, full: bool = True, force: bool = False) -> 'VeilApiResponse':
        """Remove domain instance on VeiL ECP."""
        url = self.action_url('remove/')
        body = dict(full=full, force=force)
        response = await self._post(url=url, json=body)
        return response

    async def list(self, with_vdisks: bool = True, paginator: VeilRestPaginator = None, # noqa
                   fields: list = None) -> 'VeilApiResponse':  # noqa
        """Get list of data_pools with node_id filter.

        By default get only domains with vdisks.
        """
        extra_params = dict(with_vdisks=int(with_vdisks))
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
        # TODO: фильтр для fields сделать аналогично paginator, чтобы он проверял наличие
        #  переданных полей в атрибутах сущности?
        if fields and isinstance(fields, list):
            extra_params['fields'] = ','.join(fields)

        return await super().list(paginator=paginator, extra_params=extra_params)

    async def __multi_manager(self, action: MultiManagerAction, entity_ids: list, full: bool,
                              force: bool) -> 'VeilApiResponse':
        """Multi manager with action.

        Possible actions:
            start
            shutdown
            suspend
            reboot
            resume
            delete
            migrate
        """
        url = self.base_url + 'multi-manager/'
        body = dict(full=full, force=force, entity_ids=entity_ids, action=action.value)
        response = await self._post(url=url, json=body)
        return response

    async def multi_start(self, entity_ids: list, full: bool = True, force: bool = False) -> 'VeilApiResponse':
        """Multi start domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.START, entity_ids=entity_ids, full=full,
                                          force=force)

    async def multi_shutdown(self, entity_ids: list, full: bool = True, force: bool = False) -> 'VeilApiResponse':
        """Multi shutdown domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.SHUTDOWN, entity_ids=entity_ids, full=full,
                                          force=force)

    async def multi_suspend(self, entity_ids: list, full: bool = True, force: bool = False) -> 'VeilApiResponse':
        """Multi suspend domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.SUSPEND, entity_ids=entity_ids, full=full,
                                          force=force)

    async def multi_reboot(self, entity_ids: list, full: bool = True, force: bool = False) -> 'VeilApiResponse':
        """Multi reboot domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.REBOOT, entity_ids=entity_ids, full=full,
                                          force=force)

    async def multi_resume(self, entity_ids: list, full: bool = True, force: bool = False) -> 'VeilApiResponse':
        """Multi resume domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.RESUME, entity_ids=entity_ids, full=full,
                                          force=force)

    async def multi_remove(self, entity_ids: list, full: bool = True, force: bool = False) -> 'VeilApiResponse':
        """Multi remove domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.DELETE, entity_ids=entity_ids, full=full,
                                          force=force)

    async def multi_migrate(self, entity_ids: list, full: bool = True, force: bool = False) -> 'VeilApiResponse':
        """Multi migrate domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.MIGRATE, entity_ids=entity_ids, full=full,
                                          force=force)
