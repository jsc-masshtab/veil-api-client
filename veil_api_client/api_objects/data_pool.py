# -*- coding: utf-8 -*-
"""Veil data-pool entity."""
from ..base.api_object import VeilApiObject


class VeilDataPool(VeilApiObject):
    """Veil data-pool entity.

    Attributes:
        client: https_client instance.
        datapool_id: VeiL data-pool id(uuid).
    """

    __API_OBJECT_PREFIX = 'data-pools/'

    def __init__(self, client, datapool_id: str = None) -> None:
        """Please see help(VeilDataPool) for more info."""
        super().__init__(client, api_object_id=datapool_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.description = None
        self.type = None
        self.used_space = None
        self.shared_storage = None
        self.size = None
        self.free_space = None
        self.created = None
        self.path = None
