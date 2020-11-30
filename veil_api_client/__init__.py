# -*- coding: utf-8 -*-

"""Veil api client.

for additional info see README.md
"""

__version__ = '2.0.4'

from .api_objects.domain import DomainConfiguration, DomainTcpUsb, VeilDomain, VeilGuestAgentCmd
from .base.api_cache import VeilCacheOptions
from .base.api_object import VeilRestPaginator
from .https_client import VeilClient, VeilClientSingleton, VeilRetryOptions

__all__ = (
    'VeilClient', 'VeilRestPaginator', 'DomainConfiguration', 'VeilClientSingleton', 'VeilCacheOptions',
    'VeilGuestAgentCmd', 'DomainTcpUsb', 'VeilRetryOptions', 'VeilDomain'
)

__author__ = 'Aleksey Devyatkin <a.devyatkin@mashtab.org>'
