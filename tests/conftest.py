# -*- coding: utf-8 -*-
"""Common fixtures."""
import logging

from aiohttp import web

import pytest

from veil_api_client.api_objects import VeilDomainExt
from veil_api_client.base import VeilApiObject
from veil_api_client.https_client import VeilClient as VeilClientBase


class VeilClient(VeilClientBase):
    """Overridden VeilClient for pytest-aiohttp compatibility."""

    def __init__(self, session, *args, **kwargs) -> None:
        """Please see help(VeilClient) for more info."""
        super().__init__(*args, **kwargs)
        self.__client_session = session

    @property
    def __session(self):
        """There is no need to track sessions, so we return self.session."""
        return self.__client_session


@pytest.fixture(scope='session')
def temporary_log_file(tmpdir_factory):
    """Temporary log file."""
    tmp_file_path = tmpdir_factory.mktemp('data').join('tmp.log')
    # str converting because of old Python versions
    return str(tmp_file_path)


@pytest.fixture(scope='session')
def temporary_json_file(tmpdir_factory):
    """Temporary JSON file."""
    tmp_file_path = tmpdir_factory.mktemp('data').join('cfg.json')
    # str converting because of old Python versions
    return str(tmp_file_path)


@pytest.fixture
def logger(temporary_log_file):
    """Logger instance for tests."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.FileHandler(temporary_log_file))
    return logger


@pytest.fixture(scope='session')
def server_address():
    """Server address for local tests."""
    return '127.0.0.1'


@pytest.fixture(scope='session')
def known_uid():
    """Str representation of uuid4 for future assertion."""
    return '48ee71d9-20f0-41fc-a99f-c518121a880e'


@pytest.fixture(scope='session')
def known_verbose_name():
    """Known verbose_name for future assertion."""
    return 'test Verbose name'


@pytest.fixture(scope='session')
def known_os_type():
    """Known os_type for future assertion."""
    return 'Linux'


@pytest.fixture(scope='session')
def known_domain_data(known_uid, known_verbose_name, known_os_type):
    """Known domain data fields."""
    return {
        'id': known_uid,
        'verbose_name': known_verbose_name,
        'os_type': known_os_type
    }


@pytest.fixture
def cli(loop, aiohttp_client, known_domain_data):
    """Mock object with aiohttp_client instance."""
    app = web.Application()

    async def get_handler(request):
        return web.json_response(known_domain_data)

    async def bad_get_handler(request):
        return web.json_response(
            {'errors': [{'code': '50004', 'detail': 'URL is not found.'}]},
            status=500
        )

    async def post_handler(request):
        json_data = await request.json()
        response_dict = known_domain_data
        response_dict.update(json_data)
        if request.query:
            response_dict['query_args'] = dict(request.query)
        return web.json_response(response_dict)

    async def put_handler(request):
        json_data = await request.json()
        response_dict = known_domain_data
        response_dict.update(json_data)
        if request.query:
            response_dict['query_args'] = dict(request.query)
        return web.json_response(response_dict)

    app.router.add_get(path='/cli-test', handler=get_handler)
    app.router.add_post(path='/cli-test', handler=post_handler)
    app.router.add_put(path='/cli-test', handler=put_handler)
    app.router.add_get(path='/cli-test-bad', handler=bad_get_handler)

    return loop.run_until_complete(aiohttp_client(app))


@pytest.fixture
def veil_cli(cli, server_address):
    """Mock object with VeilClient instance."""
    return VeilClient(token='jwt eyJ0', server_address=server_address, session=cli)


@pytest.fixture
def veil_cli_extra(cli, server_address):
    """Mock object with VeilClient instance with limited URL-length."""
    return VeilClient(token='jwt eyJ0',
                      server_address=server_address,
                      session=cli,
                      url_max_length=20)


@pytest.fixture
def api_object(veil_cli):
    """Mock object with VeilApiObject instance."""
    return VeilApiObject(client=veil_cli, api_object_prefix='domain/',
                         api_object_id='eafc39f3-ce6e-4db2-9d4e-1d93babcbe26')


@pytest.fixture
def api_object_domain(veil_cli):
    """Mock object with VeilDomainExt aka VeilDomain instance."""
    return VeilDomainExt(client=veil_cli,
                         api_object_id='eafc39f3-ce6e-4db2-9d4e-1d93babcbe26')
