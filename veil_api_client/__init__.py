# -*- coding: utf-8 -*-

"""Veil api client.

for additional info see README.md
"""

__version__ = '2.2.0'

from .api_objects import (DomainBackupConfiguration, DomainConfiguration, DomainTcpUsb,
                          DomainUpdateConfiguration, VeilDomainExt, VeilGuestAgentCmd)
from .base import (TagConfiguration, VeilCacheAbstractClient, VeilCacheConfiguration,
                   VeilRestPaginator, VeilTag)
from .base.utils import VeilEntityConfiguration
from .https_client import VeilClient, VeilClientSingleton, VeilRetryConfiguration

__all__ = (
    'VeilClient', 'VeilRestPaginator', 'DomainConfiguration', 'VeilClientSingleton',
    'VeilCacheConfiguration', 'TagConfiguration', 'VeilEntityConfiguration',
    'VeilGuestAgentCmd', 'DomainTcpUsb', 'VeilRetryConfiguration', 'VeilDomainExt',
    'DomainBackupConfiguration', 'VeilTag', 'VeilCacheAbstractClient',
    'DomainUpdateConfiguration'
)

__author__ = 'Aleksey Devyatkin <a.devyatkin@mashtab.org>'
