# -*- coding: utf-8 -*-

"""Veil api client.

for additional info see README.md
"""

__version__ = '2.2.0'

from .api_objects.domain import (DomainBackupConfiguration, DomainConfiguration, DomainTcpUsb,
                                 VeilDomain, VeilGuestAgentCmd, )
from .base import TagConfiguration, VeilCacheOptions, VeilRestPaginator, VeilTag
from .base.utils import VeilEntityConfiguration
from .https_client import VeilClient, VeilClientSingleton, VeilRetryConfiguration

__all__ = (
    'VeilClient', 'VeilRestPaginator', 'DomainConfiguration', 'VeilClientSingleton',
    'VeilCacheOptions', 'TagConfiguration', 'VeilEntityConfiguration',
    'VeilGuestAgentCmd', 'DomainTcpUsb', 'VeilRetryConfiguration', 'VeilDomain',
    'DomainBackupConfiguration', 'VeilTag'
)

__author__ = 'Aleksey Devyatkin <a.devyatkin@mashtab.org>'
