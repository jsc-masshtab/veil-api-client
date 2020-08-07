# -*- coding: utf-8 -*-
"""Base api object."""
from uuid import UUID

from .api_client import VeilApiClient
from .api_response import VeilApiResponse
from .descriptors import (NullableIntType, NullableStringType,
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

    def __init__(self, client, api_object_prefix: str, api_object_id: str = None) -> None:
        """Please see help(VeilApiObject) for more info."""
        # TODO: нужно иметь возможность указывать ttl
        self.__api_object_prefix = api_object_prefix
        self._client = client
        self.api_object_id = api_object_id
        self.status = None
        self.verbose_name = None

    def _update(self, attrs_dict: dict) -> None:
        """Update public class attributes ignoring property."""
        for attr in attrs_dict:
            if attr.startswith('_'):
                continue
            if hasattr(self.__class__, attr) and callable(getattr(self.__class__, attr)):
                continue
            if attr not in self.public_attrs:
                continue
            if attr in self.public_attrs and isinstance(self.public_attrs[attr], property):
                continue
            self.__setattr__(attr, attrs_dict[attr])

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
                   extra_params: dict = None) -> 'VeilApiResponse':
        """List all objects of Veil api object class."""
        params = paginator.notnull_attrs if paginator else dict()
        if extra_params:
            params.update(extra_params)
        return await self._client.get(self.base_url, extra_params=params)

    async def info(self) -> 'VeilApiResponse':
        """Get api object instance and update public attrs."""
        response = await self._client.get(self.api_object_url)
        if response.status_code == 200 and response.data:
            self._update(response.data)
        return response
