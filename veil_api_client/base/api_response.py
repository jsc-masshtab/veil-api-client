# -*- coding: utf-8 -*-
"""Veil api response."""
# TODO: generator with paginator
# TODO: можно ли работать через пагинатор с VeiL?


class VeilApiResponse:
    """VeiL api response object."""

    def __init__(self, status_code, data, headers):
        self.status_code = status_code
        self.data = data
        self.headers = headers
