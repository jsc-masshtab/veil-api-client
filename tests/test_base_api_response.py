# -*- coding: utf-8 -*-
"""Base api response test cases."""
from uuid import uuid4

from aiohttp import web

import pytest

from veil_api_client.api_objects.vdisk import VeilVDisk
from veil_api_client.base.api_object import VeilTask
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

    async def test_info_props(self):
        """Test properties and magic methods for info."""
        # Good cases
        response_value = {'k': 'value'}
        good_response = VeilApiResponse(status_code=200,
                                        data=response_value,
                                        headers=None,
                                        api_object=None)
        assert '200' in good_response.__repr__()
        assert '200: []' in good_response.__str__()
        assert good_response.value == response_value
        assert good_response.paginator_results == list()
        assert good_response.paginator_count == 0
        assert good_response.paginator_next is None
        assert good_response.paginator_previous is None
        assert good_response.success
        assert good_response.error_code == 0
        assert good_response.error_detail is None
        assert good_response.errors is None

        response = VeilApiResponse(status_code=202,
                                   data={'k': 'value', '_task': {'id': str(uuid4())}},
                                   headers=None,
                                   api_object=VeilVDisk(client=None,
                                                        api_object_id=str(uuid4())))
        assert isinstance(response.task, VeilTask)
        assert isinstance(response.response, list)
        assert isinstance(response.response[0], VeilVDisk)
        # Bad cases
        bad_response_value = {'errors': [{'code': '1000', 'detail': 'URL is not found.'}]}
        bad_response = VeilApiResponse(status_code=400,
                                       data=bad_response_value,
                                       headers=None,
                                       api_object=None)
        assert bad_response.value == dict()
        assert bad_response.paginator_results == list()
        assert bad_response.paginator_count == 0
        assert bad_response.paginator_next is None
        assert bad_response.paginator_previous is None
        assert not bad_response.success
        assert bad_response.error_code == 1000
        assert bad_response.error_detail == 'URL is not found.'

        bad_response_2 = VeilApiResponse(status_code=400,
                                         data=[],
                                         headers=None,
                                         api_object=None)
        assert bad_response_2.error_code == 50000
        assert bad_response_2.error_detail is None
        assert bad_response_2.task is None

    async def test_list_props(self):
        """Test properties and magic methods for list."""
        # Good cases
        response_value = {'id': str(uuid4())}
        response_list_value = {'results': [response_value],
                               'count': 10,
                               'next': 'https://127.0.0.1/list&page2',
                               'previous': None}
        good_response = VeilApiResponse(status_code=200,
                                        data=response_list_value,
                                        headers=None,
                                        api_object=VeilVDisk(client=None, api_object_id=None))
        assert good_response.paginator_results == [response_value]
        assert good_response.paginator_count == 10
        assert good_response.paginator_next == 'https://127.0.0.1/list&page2'
        assert good_response.paginator_previous is None
        assert good_response.value == response_list_value
        assert isinstance(good_response.response, list)
        assert isinstance(good_response.response[0], VeilVDisk)

        response = VeilApiResponse(status_code=202,
                                   data={'_task': {'id': str(uuid4())}},
                                   headers=None,
                                   api_object=VeilVDisk(client=None, api_object_id=None)
                                   )

        assert isinstance(response.task, VeilTask)

        # Bad cases
        bad_response_value = {'errors': [{'code': 'unknown', 'detail': 'URL is not found.'}]}
        bad_response = VeilApiResponse(status_code=400,
                                       data=bad_response_value,
                                       headers=None,
                                       api_object=None)
        assert bad_response.value == dict()
        assert bad_response.paginator_results == list()
        assert bad_response.error_code == 50000

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
            data="{\'errors\': [{\'detail\': \'Signature has expired.\', \'code\': \'invalid\'}]}",  # noqa: E501
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

    @staticmethod
    @veil_api_response
    async def client_response(client, fetch_response_func, **_):
        """Response from fake server converted by veil_api_response_decorator."""
        # func(client, *args, **kwargs)
        raw_response = await client.get('/')
        return await fetch_response_func(raw_response)

    async def test_api_response_200(self, aiohttp_raw_server, aiohttp_client):
        """Test Veil response 200 converter."""
        raw_server = await aiohttp_raw_server(self.api_response_200)
        test_client = await aiohttp_client(raw_server)
        response = await self.client_response(client=test_client,
                                              fetch_response_func=self.__fetch_response_data,
                                              api_object=None)
        assert isinstance(response, VeilApiResponse)
        assert response.status_code == 200

    async def test_api_response_401(self, aiohttp_raw_server, aiohttp_client):
        """Test Veil response 401 converter."""
        raw_server = await aiohttp_raw_server(self.api_response_401)
        test_client = await aiohttp_client(raw_server)
        response = await self.client_response(client=test_client,
                                              fetch_response_func=self.__fetch_response_data,
                                              api_object=None)
        assert isinstance(response, VeilApiResponse)
        assert response.status_code == 401
