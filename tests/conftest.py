# -*- coding: utf-8 -*-
"""Common fixtures."""
import logging

from async_generator import async_generator, yield_

import pytest

from veil_api_client.base.api_object import VeilApiObject
from veil_api_client.https_client import VeilClient

SERVER_ADDRESS = '127.0.0.1'


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
    return SERVER_ADDRESS


@pytest.fixture
@async_generator
async def veil_client(event_loop, server_address):
    """Mock object with VeilClient instance."""
    session = VeilClient(token='jwt eyJ0', server_address=server_address)
    await yield_(session)
    await session.close()


@pytest.fixture
def api_object(veil_client):
    """Mock object with VeilApiObject instance."""
    return VeilApiObject(client=veil_client, api_object_prefix='domain/',
                         api_object_id='eafc39f3-ce6e-4db2-9d4e-1d93babcbe26')
