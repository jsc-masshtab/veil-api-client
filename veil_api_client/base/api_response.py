# -*- coding: utf-8 -*-
"""Veil api response."""
import functools
import logging

from aiohttp.client_reqrep import ClientResponse

logger = logging.getLogger('veil-api-client.response')
logger.addHandler(logging.NullHandler())


class VeilApiResponse:
    """VeiL api response object.

    Attributes:
        status_code: http response status code.
        data: response json dictionary.
        headers: response headers.

    Properties:
        paginator_results: value of results key from response data. May presents only in list() queries.
    """

    def __init__(self, status_code, data, headers) -> None:
        """Please see help(VeilApiResponse) for more info."""
        self.status_code = status_code
        self.data = data
        self.headers = headers
        if status_code != 200:
            logger.warning('request status code is %s', status_code)
        logger.debug('response data: %s', data)

    @property
    def paginator_results(self) -> list:
        """Value of results key from response data. May presents only in list() queries."""
        # Эксперементальный блок - нет уверенности, что у VeiL все ответы такие.
        if self.status_code != 200 or not isinstance(self.data, dict) or 'results' not in self.data.keys():
            return list()
        else:
            return self.data['results']

    @property
    def value(self) -> dict:
        """Value of single-count entity from response data. May present in info() query."""
        # Эксперементальный блок - нет уверенности, что у VeiL все ответы такие.
        if self.status_code != 200 or not isinstance(self.data, dict):
            return dict()
        else:
            return self.data

    # TODO: универсальный метод возвращающий список из 1 или нескольких элементов в зависимости от запроса
    # TODO: возвращать необходжимо список или 1 объект с сущностью и ее полями


def veil_api_response_decorator(func) -> 'VeilApiResponse':
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
