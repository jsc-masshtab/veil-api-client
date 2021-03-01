# -*- coding: utf-8 -*-
"""Veil library entity."""
from typing import Optional

try:
    from aiohttp.client_reqrep import ClientResponse
except ImportError:  # pragma: no cover
    ClientResponse = None

from ..base import (VeilApiObject,
                    VeilCacheConfiguration, VeilRestPaginator, VeilRetryConfiguration)
from ..base.utils import argument_type_checker_decorator


class VeilLibrary(VeilApiObject):
    """Veil library entity.

    Attributes:
        client: https_client instance.
        api_object_id: VeiL library(file) id(uuid).
        domain: VeiL domain id(uuid). If domain is set - show only domain backups.
        datapool: VeiL datapool id(uuid).
        filename: filename on fs.
        can_be_incremental: possibility of further increment.
        path: filepath on fs.
        size: filesize (bytes).
        additional_flags:  dict with additional flags (can_be_domained, can_be_unpacked).
        assignment_type: backup, qcow or etc.
    """

    __API_OBJECT_PREFIX = 'library/'

    def __init__(self, client,
                 api_object_id: Optional[str] = None,
                 retry_opts: Optional[VeilRetryConfiguration] = None,
                 cache_opts: Optional[VeilCacheConfiguration] = None
                 ):
        """Please see help(VeilDomain) for more info."""
        super().__init__(client,
                         api_object_id=api_object_id,
                         api_object_prefix=self.__API_OBJECT_PREFIX,
                         retry_opts=retry_opts,
                         cache_opts=cache_opts)
        self.filename = None
        self.can_be_incremental = None
        self.path = None
        self.size = None
        self.additional_flags = None
        self.assignment_type = None
        self.datapool = None

    @argument_type_checker_decorator  # noqa: A003
    async def list(self,
                   domain: str = None,
                   datapool: str = None,
                   paginator: VeilRestPaginator = None,
                   extra_params: dict = None):
        """List of files on ECP VeiL."""
        params = dict()
        if domain:
            params['domain'] = domain
        if datapool:
            params['datapool'] = datapool
        if extra_params:
            params.update(extra_params)
        return await super().list(paginator=paginator, extra_params=params)
