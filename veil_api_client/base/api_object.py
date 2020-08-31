# -*- coding: utf-8 -*-
"""Base api object."""
from uuid import UUID

try:
    from aiohttp import ClientResponse
except ImportError:  # pragma: no cover
    ClientResponse = None

from .api_client import VeilApiClient
from .api_response import VeilApiResponse
from .utils import (NullableIntType, NullableStringType,
                    TypeChecker, UuidStringType, argument_type_checker_decorator)


class VeilRestPaginator:
    """VeiL Paginator interface.

    Attributes:
        name: name value pattern.
        ordering: Which field to use when ordering the results.
        limit: Number of results to return per page.
        offset: The initial index from which to return the results.
    """

    name = NullableStringType('name')
    ordering = NullableStringType('ordering')
    limit = NullableIntType('limit')
    offset = NullableIntType('offset')

    def __init__(self, name: str = None, ordering: str = None, limit: int = None, offset: int = None) -> None:
        """Please see help(VeilRestPaginator) for more info."""
        self.name = name
        self.ordering = ordering
        self.limit = limit
        self.offset = offset

    @property
    def notnull_attrs(self) -> dict:
        """Return only attributes with values."""
        return {attr: self.__dict__[attr] for attr in self.__dict__ if self.__dict__[attr]}


class VeilApiObject:
    """Base VeiL Api Object.

    Abstract class for VeiL entity description.

    Attributes:
        client: https_client instance.
        api_object_prefix: VeiL entity url postfix (domain, cluster and etc).
        api_object_id: VeiL entity id(uuid).
    """

    api_object_id = UuidStringType('api_object_id')
    _client = TypeChecker('_client', VeilApiClient)

    class __STATUS:
        """Veil api object possible statuses."""

        creating = 'CREATING'
        active = 'ACTIVE'
        failed = 'FAILED'
        deleting = 'DELETING'
        service = 'SERVICE'
        partial = 'PARTIAL'

    def __init__(self, client: VeilApiClient, api_object_prefix: str, api_object_id: str = None) -> None:
        """Please see help(VeilApiObject) for more info."""
        # TODO: нужно иметь возможность указывать ttl
        self.__api_object_prefix = api_object_prefix
        self._client = client
        self.api_object_id = api_object_id
        self.status = None
        self.verbose_name = None

    def update_public_attrs(self, attrs_dict: dict) -> None:
        """Update public class attributes ignoring property."""
        for attr in attrs_dict:
            if attr.startswith('_'):
                continue
            if hasattr(self.__class__, attr) and callable(getattr(self.__class__, attr)):
                continue
            if attr == 'id':
                # id not in public attrs, but we need to set api_object_id if it`s not set earlier.
                self.__setattr__('api_object_id', attrs_dict[attr])
                continue
            if attr not in self.public_attrs:
                continue
            if attr in self.public_attrs and isinstance(self.public_attrs[attr], property):
                continue
            self.__setattr__(attr, attrs_dict[attr])

    def copy(self):
        """Return new class instance with preconfigured parameters."""
        return self.__class__(client=self._client, api_object_id=self.api_object_id)

    async def _get(self, url: str, extra_params: dict = None) -> 'ClientResponse':
        """Layer for calling a client GET method."""
        return await self._client.get(api_object=self, url=url, extra_params=extra_params)

    async def _post(self, url: str, json: dict = None) -> 'ClientResponse':
        """Layer for calling a client POST method."""
        return await self._client.post(api_object=self, url=url, json=json)

    async def _put(self, url: str, json: dict = None) -> 'ClientResponse':
        """Layer for calling a client PUT method."""
        return await self._client.put(api_object=self, url=url, json=json)

    @property
    def public_attrs(self) -> dict:
        """Return dictionary of class public attributes and properties."""
        result_dict = dict()
        for attr in dir(self):
            if attr.startswith('_'):
                continue
            if hasattr(self.__class__, attr) and callable(getattr(self.__class__, attr)):  # noqa
                continue
            if hasattr(self.__class__, attr):
                attr_value = getattr(self.__class__, attr)
            else:
                attr_value = self.__getattribute__(attr)
            result_dict[attr] = attr_value
        return result_dict

    @property
    def task(self):
        """VeilTask entity with same client as ApiObject."""
        return VeilTask(client=self._client)

    @property
    def uuid_(self) -> UUID:
        """Convert a string with id to UUID."""
        try:
            object_id = self.api_object_id
            if not isinstance(object_id, str):
                object_id = str(object_id)  # pragma: no cover
            object_uuid = UUID(object_id)
        except (ValueError, NameError, AttributeError):  # pragma: no cover
            # Now covered by descriptors tests.
            return  # pragma: no cover
        return object_uuid

    @property
    def base_url(self) -> str:
        """Build entity full url (without id)."""
        return ''.join([self._client.base_url, self.__api_object_prefix])

    @property
    def api_object_url(self) -> str:
        """Build entity full url (with url)."""
        if not self.api_object_id:
            raise AttributeError('api_object_id is empty.')
        return self.base_url + '{}/'.format(self.api_object_id)

    @property
    def creating(self) -> bool:
        """Entity status is __STATUS.creating."""
        return self.status == self.__STATUS.creating if self.status else False

    @property
    def active(self) -> bool:
        """Entity status is __STATUS.active."""
        return self.status == self.__STATUS.active if self.status else False

    @property
    def failed(self) -> bool:
        """Entity status is __STATUS.failed."""
        return self.status == self.__STATUS.failed if self.status else False

    @property
    def deleting(self) -> bool:
        """Entity status is __STATUS.deleting."""
        return self.status == self.__STATUS.deleting if self.status else False

    @property
    def service(self) -> bool:
        """Entity status is __STATUS.service."""
        return self.status == self.__STATUS.service if self.status else False

    @property
    def partial(self) -> bool:
        """Entity status is __STATUS.partial."""
        return self.status == self.__STATUS.partial if self.status else False

    @argument_type_checker_decorator  # noqa
    async def list(self, paginator: VeilRestPaginator = None,
                   extra_params: dict = None):
        """List all objects of Veil api object class."""
        params = paginator.notnull_attrs if paginator else dict()
        if extra_params:
            params.update(extra_params)
        return await self._get(self.base_url, extra_params=params)

    async def info(self):
        """Get api object instance and update public attrs."""
        response = await self._get(self.api_object_url)
        if response.status_code == 200 and response.data:
            self.update_public_attrs(response.data)
        return response


class VeilTask(VeilApiObject):
    """Veil task entity.

    All requests sent with async=1 will be async task. Here are methods for VeiL
    tasks checking.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL task id(uuid).
    """

    __API_OBJECT_PREFIX = 'tasks/'
    task = None

    def __init__(self, client, api_object_id: str = None) -> None:
        """Please see help(VeilTask) for more info."""
        super().__init__(client, api_object_id=api_object_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.is_cancellable = None
        self.is_multitask = None
        self.progress = None
        self.error_message = None
        self.executed = None
        self.created = None
        self.name = None
        self.detail_message = None
        self.entities = None

    async def check(self) -> 'VeilApiResponse':
        """All tasks completion endpoint.

        Probably don`t need."""
        url = self.base_url + 'check/'
        response = await self._put(url)
        return response

    async def count(self) -> 'VeilApiResponse':
        """Task counters endpoint."""
        url = self.base_url + 'count/'
        response = await self._get(url)
        return response

    async def cancel(self) -> 'VeilApiResponse':
        """Exit tasks endpoint."""
        url = self.api_object_url + 'cancel/'
        response = await self._put(url)
        return response

    async def jid(self) -> 'VeilApiResponse':
        """Endpoint of receiving jid of a separate task."""
        url = self.api_object_url + 'jid/'
        response = await self._get(url)
        return response

    async def release_locks(self) -> 'VeilApiResponse':
        """Endpoint to reset locks from tasks."""
        url = self.api_object_url + 'release-locks/'
        response = await self._put(url)
        return response

    async def response(self) -> 'VeilApiResponse':
        """Endpoint of receiving a response from the node."""
        url = self.api_object_url + 'response/'
        response = await self._get(url)
        return response

    @property
    async def completed(self) -> bool:
        """Check that task is completed."""
        # url = self.api_object_id
        # extra_params = {'fields': 'status'}
        # response = await self._get(url, extra_params=extra_params)
        await self.info()
        return self.status == 'SUCCESS'
