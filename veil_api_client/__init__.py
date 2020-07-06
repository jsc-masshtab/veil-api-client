# -*- coding: utf-8 -*-

"""Veil api client.

for additional info see README.md
"""

__version__ = '2.0.0'

from .api_objects.domain import DomainConfiguration
from .base.api_object import VeilRestPaginator
from .https_client import VeilClient, VeilClientSingleton

__all__ = (
    'VeilClient', 'VeilRestPaginator', 'DomainConfiguration', 'VeilClientSingleton'
)

__author__ = 'Aleksey Devyatkin <a.devyatkin@mashtab.org>'
