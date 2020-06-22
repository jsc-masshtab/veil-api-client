# -*- coding: utf-8 -*-
"""Base api object."""
from uuid import UUID

from .utils import UuidStringType


class VeilApiObject:

    api_object_id = UuidStringType('api_object_id')

    class __STATUS:
        """Veil api object possible statuses."""

        creating = 'CREATING'
        active = 'ACTIVE'
        failed = 'FAILED'
        deleting = 'DELETING'
        service = 'SERVICE'
        partial = 'PARTIAL'

    def __init__(self, client, api_object_prefix: str, api_object_id: str = None):
        self.__api_object_prefix = api_object_prefix
        self._client = client
        self.api_object_id = api_object_id
        self.status = None
        self.verbose_name = None

    def _update(self, attrs_dict: dict):
        """Обновляет публичные атрибуты класса игнорируя property."""
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
    def uuid_(self):
        """Конвертирует строку с id в UUID."""
        try:
            object_id = self.api_object_id
            if not isinstance(object_id, str):
                object_id = str(object_id)
            object_uuid = UUID(object_id)
        except (ValueError, NameError, AttributeError):
            return
        return object_uuid

    @property
    def base_url(self):
        return ''.join([self._client.base_url, self.__api_object_prefix])

    @property
    def api_object_url(self):
        if not self.api_object_id:
            raise AttributeError('api_object_id is empty.')
        return self.base_url + '{}/'.format(self.api_object_id)

    @property
    def creating(self):
        return self.status == self.__STATUS.creating if self.status else False

    @property
    def active(self):
        return self.status == self.__STATUS.active if self.status else False

    @property
    def failed(self):
        return self.status == self.__STATUS.failed if self.status else False

    @property
    def deleting(self):
        return self.status == self.__STATUS.deleting if self.status else False

    @property
    def service(self):
        return self.status == self.__STATUS.service if self.status else False

    @property
    def partial(self):
        return self.status == self.__STATUS.partial if self.status else False

    async def list(self):  # noqa
        """List all objects of Veil api object class."""
        return await self._client.get(self.base_url)

    async def info(self):
        """Get api object instance and update public attrs."""
        response = await self._client.get(self.api_object_url)
        if response.status_code == 200 and response.data:
            self._update(response.data)
        return response
