# -*- coding: utf-8 -*-
"""Veil api response."""
import functools

from aiohttp.client_reqrep import ClientResponse


class VeilApiResponse:
    """VeiL api response object.

    Attributes:
        status_code: http response status code.
        data: response json dictionary.
        headers: response headers.
    """

    def __init__(self, status_code, data, headers):
        """Please see help(VeilApiResponse) for more info."""
        self.status_code = status_code
        self.data = data
        self.headers = headers


def veil_api_response_decorator(func):
    """Make VeilApiResponse from aiohttp.response."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        resp = await func(*args, **kwargs)
        if isinstance(resp, ClientResponse):
            async with resp:
                status_code = resp.status
                headers = resp.headers
                data = await resp.json()
            return VeilApiResponse(status_code=status_code, data=data, headers=headers)
        return resp  # pragma: no cover
    return wrapper
