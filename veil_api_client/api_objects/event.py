# -*- coding: utf-8 -*-
"""Veil event entity."""
from typing import Optional

from ..base import (VeilApiObject, VeilCacheConfiguration,
                    VeilRestPaginator, VeilRetryConfiguration)


class VeilEvent(VeilApiObject):
    """Veil event entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL event id(uuid) for extra filtering.
    """

    __API_OBJECT_PREFIX = 'events/'

    def __init__(self, client,
                 api_object_id: Optional[str] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None) -> None:
        """Please see help(VeilEvent) for more info."""
        super().__init__(client,
                         api_object_id=api_object_id,
                         api_object_prefix=self.__API_OBJECT_PREFIX,
                         retry_opts=retry_opts,
                         cache_opts=cache_opts)
        self.message = None
        self.user = None
        self.detail_message = None
        self.type = None
        self.created = None

    async def list(self,  # noqa: A003
                   user: str = None,
                   event_type: str = None,
                   paginator: VeilRestPaginator = None,
                   extra_params: dict = None):
        """List of events on ECP VeiL."""
        params = dict()
        if user:
            params['user'] = user
        if event_type:
            params['type'] = event_type
        if extra_params:
            params.update(extra_params)
        return await super().list(paginator=paginator, extra_params=params)
