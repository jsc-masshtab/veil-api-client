# -*- coding: utf-8 -*-
"""VeilClient base test cases."""
from aiohttp import ClientTimeout

import pytest

from veil_api_client import VeilClient, VeilClientSingleton, VeilRetryConfiguration
from veil_api_client.api_objects import (VeilCluster, VeilController, VeilDataPool,
                                         VeilDomainExt, VeilEvent,
                                         VeilLibrary, VeilNode, VeilResourcePool, VeilVDisk)
from veil_api_client.base import VeilTag, VeilTask

pytestmark = [pytest.mark.base]


class TestVeilClient:
    """VeilClient test cases."""

    @staticmethod
    async def good_resp_assertion(response,
                                  api_object_domain,
                                  known_uid,
                                  known_verbose_name,
                                  known_os_type):
        """Good response identical assertions."""
        assert response.success
        assert response.status_code == 200
        assert not response.errors
        assert response.error_code == 0
        assert isinstance(response.response, list)
        for response_entity in response.response:
            assert isinstance(response_entity, type(api_object_domain))
            assert response_entity.verbose_name == known_verbose_name
            assert response_entity.api_object_id == known_uid
            assert response_entity.os_type == known_os_type

    @staticmethod
    async def bad_resp_assertion(response, api_object_domain, known_uid):
        """Bad response identical assertions."""
        assert not response.success
        assert response.status_code == 500
        assert response.errors
        assert response.error_code == 50004

        assert isinstance(response.response, list)

        # The response overwrites the arguments that are in the object already,
        # so the data will be overwritten.

        for response_entity in response.response:
            assert isinstance(response_entity, type(api_object_domain))
            assert not response_entity.verbose_name
            assert response_entity.api_object_id != known_uid

    async def test_get_1(self, loop, veil_cli, api_object_domain, known_uid, known_verbose_name, known_os_type):  # noqa: E501
        """Basic get request."""
        resp = await veil_cli.get(url='/cli-test', api_object=api_object_domain)
        await self.good_resp_assertion(response=resp,
                                       api_object_domain=api_object_domain,
                                       known_uid=known_uid,
                                       known_verbose_name=known_verbose_name,
                                       known_os_type=known_os_type)

    async def test_get_2(self, loop, veil_cli, api_object_domain, known_uid, known_verbose_name):  # noqa: E501
        """Basic get request."""
        resp = await veil_cli.get(url='/cli-test-bad', api_object=api_object_domain)
        await self.bad_resp_assertion(response=resp,
                                      api_object_domain=api_object_domain,
                                      known_uid=known_uid)

    async def test_get_3(self, loop, veil_cli_extra, api_object_domain):
        """Max url request."""
        try:
            await veil_cli_extra.get(url='/cli-test-bad',
                                     api_object=api_object_domain,
                                     extra_params={'some': 'super large url'})
        except AssertionError as ex_msg:
            assert 'The maximum url length is set and exceeded' in str(ex_msg)
        else:
            raise AssertionError()

    async def test_post_1(self, loop, veil_cli, api_object_domain, known_uid, known_verbose_name, known_os_type):  # noqa: E501
        """Basic post request."""
        json_test_data = {'known_key': 'known_value'}
        resp = await veil_cli.post(url='/cli-test',
                                   api_object=api_object_domain,
                                   json_data=json_test_data)
        await self.good_resp_assertion(response=resp,
                                       api_object_domain=api_object_domain,
                                       known_uid=known_uid,
                                       known_verbose_name=known_verbose_name,
                                       known_os_type=known_os_type)

        assert 'idempotency_key' in resp.data
        assert json_test_data['known_key'] == resp.data['known_key']

    async def test_post_2(self, loop, veil_cli, api_object_domain, known_uid, known_verbose_name, known_os_type):  # noqa: E501
        """Basic post request with query args."""
        json_test_data = {'known_key': 'known_value'}
        resp = await veil_cli.post(url='/cli-test',
                                   api_object=api_object_domain,
                                   json_data=json_test_data,
                                   extra_params={'query-key': 'query-value'})
        await self.good_resp_assertion(response=resp,
                                       api_object_domain=api_object_domain,
                                       known_uid=known_uid,
                                       known_verbose_name=known_verbose_name,
                                       known_os_type=known_os_type)

        assert 'query-key' in resp.data['query_args']
        assert 'query-value' == resp.data['query_args']['query-key']

    async def test_put_1(self, loop, veil_cli, api_object_domain, known_uid, known_verbose_name, known_os_type):  # noqa: E501
        """Basic put request."""
        # idempotency key only is only in post
        json_test_data = {'known_key2': 'known_value2'}
        resp = await veil_cli.put(url='/cli-test',
                                  api_object=api_object_domain,
                                  json_data=json_test_data)
        await self.good_resp_assertion(response=resp,
                                       api_object_domain=api_object_domain,
                                       known_uid=known_uid,
                                       known_verbose_name=known_verbose_name,
                                       known_os_type=known_os_type)

    async def test_put_2(self, loop, veil_cli, api_object_domain, known_uid, known_verbose_name, known_os_type):  # noqa: E501
        """Basic put request with query args."""
        json_test_data = {'known_key2': 'known_value2'}
        resp = await veil_cli.put(url='/cli-test',
                                  api_object=api_object_domain,
                                  json_data=json_test_data,
                                  extra_params={'query-key': 'query-value'})
        await self.good_resp_assertion(response=resp,
                                       api_object_domain=api_object_domain,
                                       known_uid=known_uid,
                                       known_verbose_name=known_verbose_name,
                                       known_os_type=known_os_type)
        assert 'query-key' in resp.data['query_args']
        assert 'query-value' == resp.data['query_args']['query-key']

    async def test_domain(self, loop, veil_cli, known_uid):
        """Basic domain __init__."""
        obj = veil_cli.domain(domain_id=known_uid)
        assert isinstance(obj, VeilDomainExt)
        assert obj.api_object_id == known_uid

    async def test_controller(self, loop, veil_cli, known_uid):
        """Basic controller __init__."""
        obj = veil_cli.controller(controller_id=known_uid)
        assert isinstance(obj, VeilController)
        assert obj.api_object_id == known_uid

    async def test_resource_pool(self, loop, veil_cli, known_uid):
        """Basic resource_pool __init__."""
        obj = veil_cli.resource_pool(resource_pool_id=known_uid)
        assert isinstance(obj, VeilResourcePool)
        assert obj.api_object_id == known_uid

    async def test_cluster(self, loop, veil_cli, known_uid):
        """Basic cluster __init__."""
        obj = veil_cli.cluster(cluster_id=known_uid)
        assert isinstance(obj, VeilCluster)
        assert obj.api_object_id == known_uid

    async def test_node(self, loop, veil_cli, known_uid):
        """Basic node __init__."""
        obj = veil_cli.node(node_id=known_uid)
        assert isinstance(obj, VeilNode)
        assert obj.api_object_id == known_uid

    async def test_vdisk(self, loop, veil_cli, known_uid):
        """Basic vdisk __init__."""
        obj = veil_cli.vdisk(vdisk_id=known_uid)
        assert isinstance(obj, VeilVDisk)
        assert obj.api_object_id == known_uid

    async def test_task(self, loop, veil_cli, known_uid):
        """Basic task __init__."""
        obj = veil_cli.task(task_id=known_uid)
        assert isinstance(obj, VeilTask)
        assert obj.api_object_id == known_uid

    async def test_tag(self, loop, veil_cli, known_uid):
        """Basic tag __init__."""
        obj = veil_cli.tag(tag_id=known_uid)
        assert isinstance(obj, VeilTag)
        assert obj.api_object_id == known_uid

    async def test_library(self, loop, veil_cli, known_uid):
        """Basic library __init__."""
        obj = veil_cli.library(library_id=known_uid)
        assert isinstance(obj, VeilLibrary)
        assert obj.api_object_id == known_uid

    async def test_data_pool(self, loop, veil_cli, known_uid):
        """Basic datapool __init__."""
        obj = veil_cli.data_pool(data_pool_id=known_uid)
        assert isinstance(obj, VeilDataPool)
        assert obj.api_object_id == known_uid

    async def test_event(self, loop, veil_cli, known_uid):
        """Basic event __init__."""
        obj = veil_cli.event(event_id=known_uid)
        assert isinstance(obj, VeilEvent)
        assert obj.api_object_id == known_uid


class TestVeilClientSingleton:
    """VeilClientSingleton test cases."""

    def test_init_1(self):
        """Basic init test."""
        ins = VeilClientSingleton()
        assert ins._VeilClientSingleton__TIMEOUT == 5 * 60

    @pytest.mark.asyncio
    async def test_init_2(self):
        """Basic init test."""
        ins = VeilClientSingleton(timeout=10, cache_opts='bad')
        assert ins._VeilClientSingleton__CACHE_OPTS == 'bad'
        ins.add_client('127.0.0.1', 'jwt As')
        for _, cl in ins.instances.items():
            assert isinstance(cl, VeilClient)
            assert cl._VeilClient__cache_opts == 'bad'
        await ins.remove_client('127.0.0.1')

    @pytest.mark.asyncio
    async def test_init_3(self):
        """Basic init test."""
        ins = VeilClientSingleton(timeout=10)
        assert not ins._VeilClientSingleton__RETRY_OPTS
        ins.add_client('127.0.0.1', 'jwt As',
                       retry_opts=VeilRetryConfiguration(num_of_attempts=5),
                       timeout=50)
        for _, cl in ins.instances.items():
            assert isinstance(cl, VeilClient)
            assert isinstance(cl._VeilClient__retry_opts, VeilRetryConfiguration)
            assert cl._VeilClient__retry_opts.num_of_attempts == 5
            assert cl._VeilClient__timeout.total == 50
        await ins.remove_client('127.0.0.1')

    @pytest.mark.asyncio
    async def test_add_client_1(self):
        """Basic add_client test."""
        ins = VeilClientSingleton(timeout=10, retry_opts='bad', cache_opts='bad')
        ins.add_client('127.0.0.1',
                       'jwt As',
                       timeout=999,
                       cache_opts='new cache',
                       retry_opts='new retry',
                       url_max_length=750)
        client = ins.instances['127.0.0.1']
        assert isinstance(client._VeilClient__timeout, ClientTimeout)
        assert client._VeilClient__timeout.total == 999
        assert client._VeilClient__timeout.total != ins._VeilClientSingleton__TIMEOUT
        assert client._VeilClient__retry_opts != ins._VeilClientSingleton__RETRY_OPTS
        assert client._VeilClient__cache_opts != ins._VeilClientSingleton__CACHE_OPTS
        await ins.remove_client('127.0.0.1')
