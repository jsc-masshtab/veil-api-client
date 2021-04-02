# -*- coding: utf-8 -*-

"""Veil api client.

for additional info see README.md
"""

__version__ = '2.2.5'

from .api_objects import (DomainBackupConfiguration, DomainConfiguration, DomainTcpUsb,
                          DomainUpdateConfiguration, VeilDomainExt, VeilGuestAgentCmd)
from .base import (TagConfiguration, VeilApiObjectStatus, VeilCacheAbstractClient,
                   VeilCacheConfiguration, VeilRestPaginator, VeilTag)
from .base.utils import VeilEntityConfiguration
from .https_client import VeilClient, VeilClientSingleton, VeilRetryConfiguration

__all__ = (
    'VeilClient', 'VeilRestPaginator', 'DomainConfiguration', 'VeilClientSingleton',
    'VeilCacheConfiguration', 'TagConfiguration', 'VeilEntityConfiguration',
    'VeilGuestAgentCmd', 'DomainTcpUsb', 'VeilRetryConfiguration', 'VeilDomainExt',
    'DomainBackupConfiguration', 'VeilTag', 'VeilCacheAbstractClient',
    'DomainUpdateConfiguration', 'VeilApiObjectStatus'
)

__author__ = 'Aleksei Deviatkin <a.devyatkin@mashtab.org>, Emile Gareev <e.gareev@mashtab.org>'
