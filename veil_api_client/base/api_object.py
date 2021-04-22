# -*- coding: utf-8 -*-
"""Base api object."""
import sys
from enum import Enum
from typing import List, Optional
from uuid import UUID

try:
    from aiohttp import ClientResponse
except ImportError:  # pragma: no cover
    ClientResponse = None

from .api_cache import VeilCacheConfiguration
from .api_response import VeilApiResponse
from .utils import (HexColorType, NullableIntType, NullableStringType,
                    StringType, UuidStringType, VeilAbstractConfiguration,
                    VeilEntityConfiguration, VeilEntityConfigurationType,
                    VeilRetryConfiguration, VeilSlugType, argument_type_checker_decorator)


class VeilRestPaginator(VeilAbstractConfiguration):
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

    def __init__(self, name: Optional[str] = None,
                 ordering: Optional[str] = None,
                 limit: Optional[int] = None,
                 offset: Optional[int] = None) -> None:
        """Please see help(VeilRestPaginator) for more info."""
        self.name = name
        self.ordering = ordering
        self.limit = limit
        self.offset = offset


class VeilApiObjectStatus(str, Enum):
    """Veil api object possible statuses."""

    creating = 'CREATING'
    active = 'ACTIVE'
    failed = 'FAILED'
    deleting = 'DELETING'
    service = 'SERVICE'
    partial = 'PARTIAL'
    success = 'SUCCESS'


class VeilApiObject:
    """Base VeiL Api Object.

    Abstract class for VeiL entity description.

    Attributes:
        client: https_client instance.
        api_object_prefix: VeiL entity url postfix (domain, cluster and etc).
        api_object_id: VeiL entity id(uuid).
        retry_opts: Retry options that overrides client retry configuration.
    """

    api_object_id = UuidStringType('api_object_id')

    def __init__(self, client,
                 api_object_prefix: str,
                 api_entity_class: Optional[str] = None,
                 api_object_id: Optional[str] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None) -> None:  # noqa: A003
        """Please see help(VeilApiObject) for more info."""
        self.__api_object_prefix = api_object_prefix
        self.__api_entity_class = api_entity_class
        self._client = client
        self.api_object_id = api_object_id
        self.id = api_object_id
        self.retry_opts = retry_opts
        self.cache_opts = cache_opts
        self.status = None
        self.verbose_name = None

    def __repr__(self):
        """Original repr and additional info."""
        original_repr = super().__repr__()
        return '{} : {} : {}'.format(original_repr, self.api_object_id, self.verbose_name)

    def __str__(self):
        """Just verbose_name."""
        original_str = super().__str__()
        return '{} - {}'.format(original_str, self.__api_object_prefix)

    def update_public_attrs(self, attrs_dict: dict) -> None:
        """Update public class attributes ignoring property."""
        public_attrs = dict()
        for attr in attrs_dict:
            if attr not in self.public_attrs:
                continue
            public_attrs[attr] = attrs_dict[attr]
        self.update_or_set_public_attrs(public_attrs)

    def update_or_set_public_attrs(self, attrs_dict: dict) -> None:
        """Update or set class public attributes ignoring property."""
        for attr in attrs_dict:
            if attr.startswith('_'):
                continue
            if hasattr(self.__class__, attr) and callable(getattr(self.__class__, attr)):
                continue
            if attr == 'id':
                # id not in public attrs, but we need to set api_object_id if it`s not set earlier.  # noqa: E501
                self.__setattr__('api_object_id', attrs_dict[attr])
                continue
            if attr in self.public_attrs and isinstance(self.public_attrs[attr], property):
                continue
            self.__setattr__(attr, attrs_dict[attr])

    def copy(self):
        """Return new class instance with preconfigured parameters."""
        return self.__class__(client=self._client, api_object_id=self.api_object_id)

    async def _get(self, url: str, extra_params: Optional[dict] = None,
                   retry_opts: Optional[VeilRetryConfiguration] = None,
                   cache_opts: Optional[VeilCacheConfiguration] = None) -> 'ClientResponse':
        """Layer for calling a client GET method.

        Note:
            retry_opts will override self.retry_opts
        """
        if not retry_opts:
            retry_opts = self.retry_opts
        if not cache_opts:
            cache_opts = self.cache_opts
        return await self._client.get(api_object=self,
                                      url=url,
                                      extra_params=extra_params,
                                      retry_opts=retry_opts,
                                      cache_opts=cache_opts)

    async def _post(self, url: str,
                    json_data: Optional[dict] = None,
                    extra_params: Optional[dict] = None,
                    retry_opts: Optional[VeilRetryConfiguration] = None,
                    cache_opts: Optional[VeilCacheConfiguration] = None) -> 'ClientResponse':
        """Layer for calling a client POST method.

        Note:
            retry_opts will override self.retry_opts
        """
        if not retry_opts:
            retry_opts = self.retry_opts
        if not cache_opts:
            cache_opts = self.cache_opts
        return await self._client.post(api_object=self,
                                       url=url,
                                       json_data=json_data,
                                       extra_params=extra_params,
                                       retry_opts=retry_opts,
                                       cache_opts=cache_opts)

    async def _put(self, url: str,
                   json_data: Optional[dict] = None,
                   extra_params: Optional[dict] = None,
                   retry_opts: Optional[VeilRetryConfiguration] = None,
                   cache_opts: Optional[VeilCacheConfiguration] = None) -> 'ClientResponse':
        """Layer for calling a client PUT method.

        Note:
            retry_opts will override self.retry_opts
        """
        if not retry_opts:
            retry_opts = self.retry_opts
        if not cache_opts:
            cache_opts = self.cache_opts
        return await self._client.put(api_object=self,
                                      url=url,
                                      json_data=json_data,
                                      extra_params=extra_params,
                                      retry_opts=retry_opts,
                                      cache_opts=cache_opts)

    @property
    def api_entity_class(self):
        """Return Veil EntityType.

        Note:
            Api object prefix is a str that must contain Veil EntityType.
            EntityType is a singular word without -.
        """
        if self.__api_entity_class:
            return self.__api_entity_class
        if self.__api_object_prefix and isinstance(self.__api_object_prefix, str):
            return self.__api_object_prefix[:-2].replace('-', '')

    @property
    def public_attrs(self) -> dict:
        """Return dictionary of class public attributes and properties."""
        result_dict = dict()
        for attr in dir(self):
            if attr.startswith('_'):
                continue
            if hasattr(self.__class__, attr) and callable(getattr(self.__class__, attr)):
                continue
            if hasattr(self.__class__, attr):
                attr_value = getattr(self.__class__, attr)
            else:
                attr_value = self.__getattribute__(attr)
            result_dict[attr] = attr_value
        return result_dict

    @property
    def task(self):
        """Veil task entity with same client as ApiObject."""
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
        """Entity status is VeilApiObjectStatus.creating."""
        return self.status == VeilApiObjectStatus.creating if self.status else False

    @property
    def active(self) -> bool:
        """Entity status is VeilApiObjectStatus.active."""
        return self.status == VeilApiObjectStatus.active if self.status else False

    @property
    def failed(self) -> bool:
        """Entity status is VeilApiObjectStatus.failed."""
        return self.status == VeilApiObjectStatus.failed if self.status else False

    @property
    def deleting(self) -> bool:
        """Entity status is VeilApiObjectStatus.deleting."""
        return self.status == VeilApiObjectStatus.deleting if self.status else False

    @property
    def service(self) -> bool:
        """Entity status is VeilApiObjectStatus.service."""
        return self.status == VeilApiObjectStatus.service if self.status else False

    @property
    def partial(self) -> bool:
        """Entity status is VeilApiObjectStatus.partial."""
        return self.status == VeilApiObjectStatus.partial if self.status else False

    @argument_type_checker_decorator  # noqa: A003
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
            self.update_or_set_public_attrs(response.data)
        return response

    async def tags_list(self, paginator: VeilRestPaginator = None):
        """List of Entity tags."""
        tag = VeilTag(client=self._client,
                      retry_opts=self.retry_opts,
                      cache_opts=self.cache_opts)
        return await tag.list(paginator=paginator,
                              entity_uuid=self.api_object_id,
                              entity_class=self.api_entity_class)


class VeilTask(VeilApiObject):
    """Veil task entity.

    All requests sent with async=1 will be async task. Here are methods for VeiL
    tasks checking.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL task id(uuid).
        retry_opts: Retry options that overrides client retry configuration.
    """

    __API_OBJECT_PREFIX = 'tasks/'
    task = None

    def __init__(self, client, api_object_id: Optional[str] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None) -> None:
        """Please see help(VeilTask) for more info."""
        super().__init__(client,
                         api_object_id=api_object_id,
                         api_object_prefix=self.__API_OBJECT_PREFIX,
                         retry_opts=retry_opts,
                         cache_opts=cache_opts)
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

        Probably don`t need.
        """
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
    async def success(self) -> bool:
        """Check that task is completed."""
        print(
            '\nWARNING: success scheduled for removal in 2.3.0 '
            'use is_success method.\n',
            file=sys.stderr,
        )
        return self.is_success()

    async def is_success(self) -> bool:
        """Check that task is completed."""
        await self.info()
        return self.status == VeilApiObjectStatus.success

    @property
    async def failed(self) -> bool:
        """Check that task is failed."""
        print(
            '\nWARNING: failed scheduled for removal in 2.3.0 '
            'use is_failed method.\n',
            file=sys.stderr,
        )
        return await self.is_failed()

    async def is_failed(self) -> bool:
        """Check that task is failed."""
        await self.info()
        return self.status == VeilApiObjectStatus.failed

    @property
    async def finished(self) -> bool:
        """Check that task is finished."""
        print(
            '\nWARNING: finished scheduled for removal in 2.3.0 '
            'use is_finished method.\n',
            file=sys.stderr,
        )
        return await self.is_finished()

    async def is_finished(self) -> bool:
        """Check that task is finished."""
        # есть поле progress, но на него лучше не смотреть
        await self.info()
        return self.status in (VeilApiObjectStatus.failed, VeilApiObjectStatus.success)

    @property
    def first_entity(self) -> dict:
        """First element of Task.entities dictionary."""
        if self.entities and isinstance(self.entities, dict):
            return next(iter(self.entities))
        return None

    @argument_type_checker_decorator  # noqa: A003
    async def list(self, paginator: VeilRestPaginator = None,
                   extra_params: dict = None,
                   parent: str = None,
                   status: VeilApiObjectStatus = None):
        """List all tasks/subtasks of Veil api object class."""
        params = dict()
        if extra_params:
            params.update(extra_params)
        if parent:
            params['parent'] = parent
        if status:
            params['status'] = status.value
        return await super().list(paginator=paginator, extra_params=params)


class TagConfiguration(VeilAbstractConfiguration):
    """Simplified Veil tag description.

    Attributes:
        verbose_name: domain verbose name.
        slug: VeiL slug str.
        colour: hex-color str (can be null, default is #c0ffee).
    """

    verbose_name = StringType('verbose_name')
    colour = HexColorType('colour')
    slug = VeilSlugType('slug')

    def __init__(self,
                 verbose_name: str,
                 slug: str,
                 colour: Optional[str] = None
                 ) -> None:
        """Please see help(TagConfiguration) for more info."""
        self.verbose_name = verbose_name
        self.slug = slug
        self.colour = colour


class VeilTag(VeilApiObject):
    """Veil tag entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL node id(uuid).
    """

    __API_OBJECT_PREFIX = 'tags/'

    ui_entities = VeilEntityConfigurationType('ui_entities')

    def __init__(self, client,
                 api_object_id: Optional[str] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None) -> None:
        """Please see help(VeilNode) for more info."""
        super().__init__(client,
                         api_object_id=api_object_id,
                         api_object_prefix=self.__API_OBJECT_PREFIX,
                         retry_opts=retry_opts,
                         cache_opts=cache_opts)
        self.slug = None
        self.colour = None
        self.ui_entities = None

    @property
    def color(self):
        """American variant."""
        return self.colour

    def action_url(self, action: str) -> str:
        """Build domain action full url."""
        return self.api_object_url + action

    @argument_type_checker_decorator
    async def create(self, tag_configuration: TagConfiguration) -> 'ClientResponse':
        """Run tag create on VeiL ECP."""
        response = await self._post(url=self.base_url,
                                    json_data=tag_configuration.notnull_attrs)
        return response

    async def update(self,
                     verbose_name: Optional[str] = None,
                     colour: Optional[str] = None) -> 'ClientResponse':
        """Run tag update on VeiL ECP."""
        if not verbose_name and not colour:
            return
        update_dict = dict()
        if verbose_name:
            TagConfiguration(verbose_name=verbose_name, slug='empty')
            update_dict['verbose_name'] = verbose_name
        if colour:
            TagConfiguration(colour=colour, slug='empty', verbose_name='empty')
            update_dict['colour'] = colour
        response = await self._put(url=self.api_object_url,
                                   json_data=update_dict)
        return response

    async def remove(self) -> 'ClientResponse':
        """Remove tag instance on VeiL ECP."""
        url = self.action_url('remove/')
        response = await self._post(url=url)
        return response

    @argument_type_checker_decorator
    async def add_entity(self, entity_configuration: VeilEntityConfiguration):
        """Add a Tag to a VeiL Entity."""
        url = self.action_url('add-entity/')
        response = await self._post(url=url, json_data=entity_configuration.notnull_attrs)
        return response

    @staticmethod
    def convert_entities(entities: List[VeilEntityConfiguration]) -> dict:
        """Make VeiL entity dict."""
        entity_uuids = list({entity.entity_uuid for entity in entities})
        return {'entity_class': entities[0].entity_class,
                'entity_uuids': entity_uuids}

    async def add_entities(self, entities_conf: List[VeilEntityConfiguration]):
        """Add a Tag to a VeiL Entities."""
        url = self.action_url('add-entities/')
        data = self.convert_entities(entities_conf)
        response = await self._post(url=url, json_data=data)
        return response

    @argument_type_checker_decorator
    async def remove_entity(self, entity_configuration: VeilEntityConfiguration):
        """Remove a Tag from a VeiL Entity."""
        url = self.action_url('remove-entity/')
        response = await self._post(url=url, json_data=entity_configuration.notnull_attrs)
        return response

    async def remove_entities(self, entities_conf: List[VeilEntityConfiguration]):
        """Remove a Tag from a VeiL Entities."""
        url = self.action_url('remove-entities/')
        data = self.convert_entities(entities_conf)
        response = await self._post(url=url, json_data=data)
        return response

    @argument_type_checker_decorator  # noqa: A003
    async def list(self,
                   entity_uuid: Optional[str] = None,
                   entity_class: Optional[str] = None,
                   paginator: VeilRestPaginator = None,
                   extra_params: dict = None,
                   name: Optional[str] = None):
        """List of tags on ECP VeiL."""
        params = dict()
        if self.slug:
            params['slug'] = self.slug
        if entity_uuid:
            params['entity_uuid'] = entity_uuid
        if entity_class:
            params['entity_class'] = entity_class
        if extra_params:
            params.update(extra_params)
        if name:
            params['name'] = name
        return await super().list(paginator=paginator, extra_params=params)
