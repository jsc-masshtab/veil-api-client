# -*- coding: utf-8 -*-
"""Veil domain entity."""
import sys
from enum import Enum, IntEnum
from typing import List, Optional
from uuid import uuid4

try:
    from aiohttp.client_reqrep import ClientResponse
except ImportError:  # pragma: no cover
    ClientResponse = None

from ..base import (VeilApiObject, VeilCacheConfiguration,
                    VeilRestPaginator, VeilRetryConfiguration)
from ..base.utils import (BoolType, NullableBoolType, NullableStringType,
                          NullableUuidStringType, StringType,
                          UuidStringType, VeilConfiguration,
                          argument_type_checker_decorator)


class DomainConfiguration(VeilConfiguration):
    """Simplified Veil domain description.

    Structure for VeiL domain copy.
    (resource_pool) and (node + datapool) are mutually exclusive parameters -> see mutually_check method  # noqa: E501


    Attributes:
        verbose_name: domain verbose name.
        resource_pool: VeiL resource pool id(uuid).
        node: VeiL node id(uuid).
        datapool: VeiL data-pool id(uuid).
        parent: VeiL parent domain id(uuid).
        thin: created domain should be a thin clone of parent domain.
    """

    verbose_name = StringType('verbose_name')
    resource_pool = NullableUuidStringType('resource_pool')
    node = NullableUuidStringType('node')
    datapool = NullableUuidStringType('datapool')
    parent = UuidStringType('parent')
    thin = BoolType('thin')

    def __init__(self, verbose_name: str,
                 parent: str,
                 resource_pool: Optional[str] = None,
                 node: Optional[str] = None,
                 datapool: Optional[str] = None,
                 thin: bool = True,
                 count: int = 1
                 ) -> None:
        """Please see help(DomainConfiguration) for more info."""
        self.resource_pool = resource_pool
        self.node = node
        self.datapool = datapool
        self.mutually_check()
        self.verbose_name = verbose_name
        self.parent = parent
        self.thin = thin
        self.count = count
        self.domains_ids = [str(uuid4()) for i in range(count)]

    def mutually_check(self):
        """Validate mutually exclusive parameters.

        (resource_pool) and (node + datapool) are mutually exclusive parameters, so only one pair can be filled.  # noqa: E501
        """
        if self.resource_pool and (self.node or self.datapool):
            raise ValueError(
                '{} and ({} + {}) are mutually exclusive parameters, so only one pair can be filled.'.format(  # noqa: E501
                    self.resource_pool, self.node, self.datapool))


class DomainUpdateConfiguration(VeilConfiguration):
    """Simplified Veil DomainUpdate description.

    Attributes:
        verbose_name: domain verbose name.
        description: domain description.
        os_type: domain os_type.
        os_version: domain os_version.
        tablet: tablet switcher.
        start_on_boot: start on boot switcher.
        spice_stream: spice stream switcher.
    """

    verbose_name = NullableStringType('verbose_name')
    description = NullableStringType('description')
    os_type = NullableStringType('os_type')
    os_version = NullableStringType('os_version')
    tablet = NullableBoolType('tablet')
    start_on_boot = NullableBoolType('start_on_boot')
    spice_stream = NullableBoolType('spice_stream')

    def __init__(self,
                 verbose_name: Optional[str] = None,
                 description: Optional[str] = None,
                 os_type: Optional[str] = None,
                 os_version: Optional[str] = None,
                 tablet: Optional[bool] = None,
                 start_on_boot: Optional[bool] = None,
                 spice_stream: Optional[bool] = None):
        """Please see help(DomainUpdateConfiguration) for more info."""
        self.verbose_name = verbose_name
        self.description = description
        self.os_type = os_type
        self.os_version = os_version
        self.tablet = tablet
        self.start_on_boot = start_on_boot
        self.spice_stream = spice_stream
        self.no_empty_check()

    def no_empty_check(self):
        """Checking that there is something to change."""  # noqa: D401
        if not self.notnull_attrs:
            raise ValueError(
                'All attributes are empty. Choose at least something.')


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


class DomainOsType:
    """Possible domain os types."""

    WIN = 'Windows'
    LINUX = 'Linux'
    OTHER = 'Other'


class DomainTcpUsb:
    """Domain TCP USB device.

    Attributes:
        host: IP адрес клиента с которого будет проброшено устройство.
        service: Порт клиента с которого будет проброшено устройство.
    """

    def __init__(self, host: str, service: int):
        """Please see help(DomainTcpUsb) for more info."""
        self.host = host
        self.service = service


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
    """Guest utils attributes."""

    def __init__(self,
                 veil_state: bool = False,
                 qemu_state: bool = False,
                 version: Optional[str] = None,
                 hostname: Optional[str] = None,
                 ipv4: Optional[list] = None,
                 **_) -> None:
        """Please see help(DomainGuestUtils) for more info."""
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

    @property
    def apipa_problem(self):
        """All ipv4 addresses in 169.254.*.*.

        Regex expression works dramatically slower.
        """
        apipa_case = '169.254.'
        if not isinstance(self.ipv4, list):
            return None
        if len(self.ipv4) == 0:
            return None
        return all(isinstance(ip, str) and apipa_case in ip for ip in self.ipv4)


class DomainBackupConfiguration(VeilConfiguration):
    """Domain backup options.

    Attributes:
        datapool: datapool_uid on which the backup will be created.
        backup: backup_uid of previous backup file with activated can_be_incremental.
        can_be_incremental: create a backup with the possibility of further increment.
        increment: increments the last of the available backups with the ability to increment,
            if there are none, then creates a new incremental backup.
        exclude_iso: exclude attached to Domain (VM) ISO from backup.

    Note:
        1. for thin-clones backup mechanism prohibited on VeiL ECP.
        2. datapool may be set only if backup is empty
    """

    datapool = NullableUuidStringType('datapool')
    backup = NullableUuidStringType('datapool')
    can_be_incremental = BoolType('can_be_incremental')
    increment = BoolType('increment')
    exclude_iso = BoolType('exclude_iso')

    def __init__(self,
                 datapool: Optional[str] = None,
                 backup: Optional[str] = None,
                 can_be_incremental: Optional[bool] = False,
                 increment: Optional[bool] = False,
                 exclude_iso: Optional[bool] = True,
                 **_) -> None:
        """Please see help(VeilDomain) for more info.

        :param _: may be save_files, limit_days - only for scheduled jobs. Ignored in client.
        """
        self.datapool = datapool
        self.backup = backup
        self.can_be_incremental = can_be_incremental
        self.increment = increment
        self.exclude_iso = exclude_iso


class VeilDomain(VeilApiObject):
    """Veil domain entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL domain id(uuid).
        resource_pool: Veil resource-pool id(uuid) for extra filtering.
        cluster_id:  VeiL cluster id(uuid) for extra filtering.
        node_id:  VeiL node id(uuid) for extra filtering.
        data_pool_id:  VeiL data-pool id(uuid) for extra filtering.
        template:  VeiL template sign. Int because of ujson limitations (only str or int).
    """

    __API_OBJECT_PREFIX = 'domains/'

    def __init__(self, client,
                 api_object_id: Optional[str] = None,
                 resource_pool: Optional[str] = None,
                 cluster_id: Optional[str] = None,
                 node_id: Optional[str] = None,
                 data_pool_id: Optional[str] = None,
                 template: Optional[int] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None) -> None:
        """Please see help(VeilDomain) for more info.

        Arguments:
            template: Boolean int (0|1).
        """
        super().__init__(client,
                         api_object_id=api_object_id,
                         api_object_prefix=self.__API_OBJECT_PREFIX,
                         retry_opts=retry_opts,
                         cache_opts=cache_opts)
        self.remote_access = None
        self.verbose_name = None
        self.node = None
        self.parent = None
        self.remote_access_port = None
        self.real_remote_access_port = None
        self.graphics_password = None
        self.template = template
        self.os_type = None
        self.os_version = None
        self.user_power_state = 0
        self.guest_utils = None
        self.cpu_topology = None
        self.cpu_count = None
        self.tags = None
        self.owners = None
        self.sound = None
        self.cpu_type = None
        self.memory_count = None
        self.vdisks = None
        self.video = None
        self.is_ova = None
        self.cdroms = None
        # resource_pool, cluster_id, node_id or data_pool_id can be UUID.
        self.resource_pool = str(resource_pool) if resource_pool else None
        self.cluster_id = str(cluster_id) if cluster_id else None
        self.node_id = str(node_id) if node_id else None
        self.data_pool_id = str(data_pool_id) if data_pool_id else None

    @property
    def cpu_count_prop(self):
        """Get cpu_count from cpu_topology dict or self.cpu_count."""
        if isinstance(self.cpu_topology, dict) and self.cpu_topology.get('cpu_count'):
            return self.cpu_topology['cpu_count']
        return self.cpu_count

    @property
    def parent_name(self):
        """Get parent Domain name."""
        if isinstance(self.parent, dict):
            return self.parent.get('verbose_name')

    @property
    def parent_uuid(self):
        """Get parent Domain UUID."""
        if isinstance(self.parent, dict):
            return self.parent.get('id')

    @property
    def guest_agent(self):
        """Verbose domain guest utils."""
        return DomainGuestUtils(**self.guest_utils) if self.guest_utils else None

    @property
    def qemu_state(self):
        """Guest agent qemu state."""
        return self.guest_agent.qemu_state if self.guest_agent else None

    @property
    def first_ipv4(self):
        """First ipv4 address."""
        return self.guest_agent.first_ipv4_ip if self.guest_agent else None

    @property
    def power_state(self):
        """Verbose domain power state."""
        return DomainPowerState(self.user_power_state)

    @property
    def powered(self):
        """Domain is power state is ON."""
        return self.power_state == DomainPowerState.ON

    @property
    def os_windows(self):
        """Domain (VM) has Windows OS."""
        return self.os_type == DomainOsType.WIN

    @property
    def hostname(self):
        """Guest utils hostname value."""
        return self.guest_agent.hostname if self.guest_agent else None

    @property
    def apipa_problem(self):
        """Guest utils apipa_problem value."""
        return self.guest_agent.apipa_problem if self.guest_agent else None

    @property
    async def in_ad(self):
        """Windows domain (VM) already in AD."""
        print(
            '\nWARNING: in_ad scheduled for removal in 2.3.0 '
            'use is_in_ad method.\n',
            file=sys.stderr,
        )
        return await self.is_in_ad()

    async def is_in_ad(self) -> bool:
        """Windows domain (VM) already in AD."""
        qemu_guest_command = {'path': 'powershell.exe',
                              'arg': ['(Get-WmiObject Win32_ComputerSystem).PartOfDomain']}
        response = await self.guest_command(qemu_cmd='guest-exec', f_args=qemu_guest_command)
        if response.status_code == 200 and response.value:
            guest_exec_response = response.value.get('guest-exec', dict()).get('out-data', 'False')  # noqa: E501
            if isinstance(guest_exec_response, str):
                guest_exec_response = guest_exec_response.strip()
                return guest_exec_response == 'True'
        return False

    def action_url(self, action: str) -> str:
        """Build domain action full url."""
        return self.api_object_url + action

    @argument_type_checker_decorator
    async def guest_command(self, veil_cmd: VeilGuestAgentCmd = None,
                            qemu_cmd: str = None,
                            f_args: dict = None,
                            timeout: int = 5):
        """Guest agent commands endpoint."""
        url = self.api_object_url + 'guest-command/'
        body = dict()
        if veil_cmd:
            body['veil_cmd'] = veil_cmd.value
        if qemu_cmd:
            body['qemu_cmd'] = qemu_cmd
        if f_args:
            body['fargs'] = f_args
        if timeout:
            body['timeout'] = timeout
        response = await self._post(url=url, json_data=body)
        return response

    async def set_hostname(self, hostname: str = None):
        """Set domain hostname on VeiL ECP."""
        url = self.api_object_url + 'set-hostname/'
        domain_hostname = hostname if hostname else self.verbose_name
        body = dict(hostname=domain_hostname)
        response = await self._post(url=url, json_data=body)
        return response

    async def add_to_ad(self,
                        domain_name: str,
                        login: str,
                        password: str,
                        restart: bool = True,
                        new_name: Optional[str] = None) -> 'ClientResponse':
        """Add domain (VM) to AD.

        domain_name: str Specifies the domain to which the computers are added
        login: str AD user which can add VM to domain
        password: str AD user password
        restart: bool restart VM that was added to the domain or workgroup
        new_name: str Specifies a new name for the computer in the new domain
        """
        url = self.api_object_url + 'add-to-ad/'
        body = dict(domainname=domain_name, login=login, password=password)
        if restart:
            body['restart'] = 1
        if new_name:
            body['newname'] = new_name
        response = await self._post(url=url, json_data=body)
        return response

    async def rm_from_ad(self,
                         login: str,
                         password: str,
                         restart: bool = True) -> 'ClientResponse':
        """Remove domain (VM) from AD."""
        url = self.api_object_url + 'rm-from-ad/'
        body = dict(login=login, password=password)
        if restart:
            body['restart'] = 1
        response = await self._post(url=url, json_data=body)
        return response

    async def add_to_ad_group(self, computer_name: str,
                              domain_username: str,
                              domain_password: str,
                              cn_pattern: str):
        """Add a domain to one or more Active Directory groups."""
        print(
            '\nWARNING: add_to_ad_group method scheduled for removal in 2.3 '
            'use your own LDAP command, like '
            'extend.microsoft.add_members_to_groups\n',
            file=sys.stderr,
        )
        credential_value = '$(New-Object System.Management.Automation.PsCredential("{}", \
                                    $(ConvertTo-SecureString -String "{}" -AsPlainText -Force)))'.format(  # noqa: E501
            domain_username, domain_password)
        get_computer_filter = "Get-ADComputer -Identity '{}' -Properties 'SID' -Credential {}".format(computer_name,  # noqa: E501
                                                                                                      credential_value)  # noqa: E501
        add_group_filter = "Add-ADPrincipalGroupMembership -MemberOf '{}' -Credential {}".format(cn_pattern,  # noqa: E501
                                                                                                 credential_value)  # noqa: E501
        qemu_guest_command = {'path': 'powershell.exe', 'arg': [get_computer_filter, '|', add_group_filter]}  # noqa: E501
        return await self.guest_command(qemu_cmd='guest-exec', f_args=qemu_guest_command)

    async def attach_usb(self, action_type: Optional[str] = None,
                         usb: Optional[dict] = None,
                         usb_controller: Optional[dict] = None,
                         tcp_usb: Optional[DomainTcpUsb] = None,
                         no_task: bool = False):
        """Attach usb devices to VM."""
        if action_type is None:
            action_type = 'tcp_usb_device'
        url = self.api_object_url + 'attach-usb/'
        body = dict(action_type=action_type)
        if usb and isinstance(usb, dict):
            body['usb'] = usb
        if usb_controller and isinstance(usb_controller, dict):
            body['usb_controller'] = usb_controller
        if tcp_usb:
            body['tcp_usb'] = tcp_usb.__dict__
        extra_params = {'async': 0} if no_task else None
        response = await self._post(url=url, json_data=body, extra_params=extra_params)
        return response

    async def detach_usb(self, action_type: Optional[str] = None,
                         controller_order: Optional[int] = None,
                         usb: Optional[str] = None,
                         remove_all: bool = True):
        """Detach usb devices from VM."""
        if action_type is None:
            action_type = 'tcp_usb_device'
        url = self.api_object_url + 'detach-usb/'
        body = dict(action_type=action_type)
        if controller_order and isinstance(controller_order, int):
            body['controller_order'] = controller_order
        if usb and isinstance(usb, str):
            body['usb'] = usb
        if remove_all:
            body['remove_all'] = 1
        response = await self._post(url=url, json_data=body)
        return response

    async def start(self, force: bool = False) -> 'ClientResponse':
        """Send domain action 'start'."""
        url = self.action_url('start/')
        body = dict(force=force)
        response = await self._post(url=url, json_data=body)
        return response

    async def reboot(self, force: bool = False) -> 'ClientResponse':
        """Send domain action 'reboot'."""
        url = self.action_url('reboot/')
        body = dict(force=force)
        response = await self._post(url=url, json_data=body)
        return response

    async def suspend(self, force: bool = False) -> 'ClientResponse':
        """Send domain action 'suspend'."""
        url = self.action_url('suspend/')
        body = dict(force=force)
        response = await self._post(url=url, json_data=body)
        return response

    async def reset(self, force: bool = False) -> 'ClientResponse':
        """Send domain action 'reset'."""
        url = self.action_url('reset/')
        body = dict(force=force)
        response = await self._post(url=url, json_data=body)
        return response

    async def shutdown(self, force: bool = False) -> 'ClientResponse':
        """Send domain action 'shutdown'."""
        url = self.action_url('shutdown/')
        body = dict(force=force)
        response = await self._post(url=url, json_data=body)
        return response

    async def resume(self, force: bool = False) -> 'ClientResponse':
        """Send domain action 'resume'."""
        url = self.action_url('resume/')
        body = dict(force=force)
        response = await self._post(url=url, json_data=body)
        return response

    async def remote_access_action(self, enable: bool = True) -> 'ClientResponse':
        """Send domain action 'remote-action'."""
        url = self.api_object_url + 'remote-access/'
        body = dict(remote_access=enable)
        response = await self._post(url, json_data=body)
        return response

    async def enable_remote_access(self) -> 'ClientResponse':
        """Enable domain remote-access."""
        return await self.remote_access_action(enable=True)

    async def disable_remote_access(self) -> 'ClientResponse':
        """Disable domain remote-access."""
        return await self.remote_access_action(enable=False)

    @argument_type_checker_decorator
    async def create(self, domain_configuration: DomainConfiguration) -> 'ClientResponse':
        """Run multi-create-domain on VeiL ECP."""
        url = self.base_url + 'multi-create-domain/'
        response = await self._post(url=url, json_data=domain_configuration.notnull_attrs)
        return response

    @argument_type_checker_decorator
    async def update(self,
                     domain_update_configuration: DomainUpdateConfiguration) -> 'ClientResponse':  # noqa: E501
        """Run VeiL ECP domain update endpoint."""
        url = self.api_object_url
        response = await self._put(url=url,
                                   json_data=domain_update_configuration.notnull_attrs)
        return response

    async def update_verbose_name(self, verbose_name: str):
        """Interface for Veil ECP domain update endpoint."""
        conf = DomainUpdateConfiguration(verbose_name=verbose_name)
        return await self.update(domain_update_configuration=conf)

    async def remove(self, full: bool = True, force: bool = False) -> 'ClientResponse':
        """Remove domain instance on VeiL ECP."""
        url = self.action_url('remove/')
        body = dict(full=full, force=force)
        response = await self._post(url=url, json_data=body)
        return response

    async def list(self, with_vdisks: bool = True,  # noqa: A003
                   paginator: VeilRestPaginator = None,
                   fields: List[str] = None,
                   params: dict = None) -> 'ClientResponse':
        """Get list of data_pools with node_id filter.

        By default get only domains with vdisks.
        """
        extra_params = dict(with_vdisks=int(with_vdisks))
        if self.resource_pool:
            extra_params['resource_pool'] = self.resource_pool
        if self.cluster_id:
            extra_params['cluster'] = self.cluster_id
        if self.node_id:
            extra_params['node'] = self.node_id
        if self.data_pool_id:
            extra_params['datapool'] = self.data_pool_id
        if isinstance(self.template, bool):
            # ujson can`t work with booleans
            extra_params['template'] = int(self.template)
        elif isinstance(self.template, int):
            extra_params['template'] = self.template
        # Additional request parameters
        if fields and isinstance(fields, list):
            extra_params['fields'] = ','.join(fields)
        if params:
            extra_params.update(params)
        return await super().list(paginator=paginator, extra_params=extra_params)

    async def __multi_manager(self, action: MultiManagerAction,
                              entity_ids: List[str],
                              full: bool,
                              force: bool) -> 'ClientResponse':
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
        response = await self._post(url=url, json_data=body)
        return response

    async def multi_start(self, entity_ids: List[str],
                          full: bool = True,
                          force: bool = False) -> 'ClientResponse':
        """Multi start domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.START,
                                          entity_ids=entity_ids,
                                          full=full,
                                          force=force)

    async def multi_shutdown(self, entity_ids: List[str],
                             full: bool = True,
                             force: bool = False) -> 'ClientResponse':
        """Multi shutdown domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.SHUTDOWN,
                                          entity_ids=entity_ids,
                                          full=full,
                                          force=force)

    async def multi_suspend(self, entity_ids: List[str],
                            full: bool = True,
                            force: bool = False) -> 'ClientResponse':
        """Multi suspend domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.SUSPEND,
                                          entity_ids=entity_ids,
                                          full=full,
                                          force=force)

    async def multi_reboot(self, entity_ids: List[str],
                           full: bool = True,
                           force: bool = False) -> 'ClientResponse':
        """Multi reboot domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.REBOOT,
                                          entity_ids=entity_ids,
                                          full=full,
                                          force=force)

    async def multi_resume(self, entity_ids: List[str],
                           full: bool = True,
                           force: bool = False) -> 'ClientResponse':  # noqa: E501
        """Multi resume domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.RESUME,
                                          entity_ids=entity_ids,
                                          full=full,
                                          force=force)

    async def multi_remove(self, entity_ids: List[str],
                           full: bool = True,
                           force: bool = False) -> 'ClientResponse':
        """Multi remove domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.DELETE,
                                          entity_ids=entity_ids,
                                          full=full,
                                          force=force)

    async def multi_migrate(self, entity_ids: List[str],
                            full: bool = True,
                            force: bool = False) -> 'ClientResponse':
        """Multi migrate domain instance on VeiL ECP."""
        return await self.__multi_manager(action=MultiManagerAction.MIGRATE,
                                          entity_ids=entity_ids,
                                          full=full,
                                          force=force)

    async def backup(self, configuration: DomainBackupConfiguration):
        """Create domain backup."""
        url = ''.join([self.base_url, 'backup/'])
        data = configuration.notnull_attrs
        data['domain'] = self.api_object_id
        return await self._post(url=url, json_data=data)

    async def show_backup(self, file_id: str):
        """A serialized VM representation from a VeiL ECP or OVA backup."""  # noqa: D401
        url = ''.join([self.base_url, 'show-backup/'])
        data = {'file': file_id}
        return await self._post(url=url, json_data=data)

    async def automated_restore(self, file_id: str, node_id: str, datapool_id: str = None):
        """Automatically restore VM from backup."""
        url = ''.join([self.base_url, 'automated-restore/'])
        data = {'file': file_id, 'node': node_id}
        if datapool_id:
            data['datapool'] = datapool_id
        return await self._post(url=url, json_data=data)

    async def attach_veil_utils_iso(self) -> 'ClientResponse':
        """Mount veil utils image to domain."""
        url = self.api_object_url + 'attach-veil-utils-iso/'
        return await self._post(url=url)

    async def change_template(self) -> 'ClientResponse':
        """Change template for domain and template's thin clones."""
        url = self.api_object_url + 'change-template/'
        response = await self._post(url=url)
        return response
