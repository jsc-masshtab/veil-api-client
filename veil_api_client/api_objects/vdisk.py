# -*- coding: utf-8 -*-
"""Veil node entity."""
from ..base.api_object import VeilApiObject


class VeilVDisk(VeilApiObject):
    """Veil vdisk entity.

    Attributes:
        client: https_client instance.
        vdisk_id: VeiL vdisk id(uuid).
    """

    __API_OBJECT_PREFIX = 'vdisks/'

    def __init__(self, client, vdisk_id: str = None):
        """Please see help(VeilVDisk) for more info."""
        super().__init__(client, api_object_id=vdisk_id, api_object_prefix=self.__API_OBJECT_PREFIX)
        self.size = None
        self.datapool = None
        self.domain = None
        self.hints = None
        self.shareable = None
