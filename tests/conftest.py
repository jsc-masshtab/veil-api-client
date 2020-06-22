# -*- coding: utf-8 -*-
"""Common fixtures."""
import logging

import pytest


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
