# -*- coding: utf-8 -*-
"""Base api response test cases."""
from aiohttp import web

import pytest

from veil_api_client.base.api_response import VeilApiResponse
from veil_api_client.base.utils import veil_api_response


pytestmark = [pytest.mark.base]


class TestVeilApiResponse:
    """VeilApiResponse test cases."""

    def test_init(self):
        """Veil api response init test case."""
        try:
            obj = VeilApiResponse(status_code=200, data=None, headers=None, api_object=None)
        except TypeError:
            raise AssertionError()
        else:
            assert isinstance(obj, VeilApiResponse)

    @staticmethod
    async def api_response_200(request):
        """Fake VeiL ECP response."""
        return web.json_response(
            data={'k': 'v'},
            status=200)

    @staticmethod
    async def api_response_401(request):
        """Fake VeiL ECP response."""
        return web.json_response(
            data="{\'errors\': [{\'detail\': \'Signature has expired.\', \'code\': \'invalid\'}]}",
            status=401)

    @staticmethod
    async def __fetch_response_data(response):
        """Collect all response attributes."""
        # Collect response data
        async with response:
            status_code = response.status
            headers = response.headers
            data = await response.json()
        return dict(status_code=status_code, headers=dict(headers), data=data)

    @veil_api_response
    async def client_response(self, client):
        """Response from fake server converted by veil_api_response_decorator."""
        raw_response = await client.get('/')
        return await self.__fetch_response_data(raw_response)

    async def test_api_response_200(self, aiohttp_raw_server, aiohttp_client):
        """Test Veil response 200 converter."""
        raw_server = await aiohttp_raw_server(self.api_response_200)
        client = await aiohttp_client(raw_server)
        response = await self.client_response(client)
        assert isinstance(response, VeilApiResponse)
        assert response.status_code == 200

    async def test_api_response_401(self, aiohttp_raw_server, aiohttp_client):
        """Test Veil response 401 converter."""
        raw_server = await aiohttp_raw_server(self.api_response_401)
        client = await aiohttp_client(raw_server)
        response = await self.client_response(client)
        assert isinstance(response, VeilApiResponse)
        assert response.status_code == 401
