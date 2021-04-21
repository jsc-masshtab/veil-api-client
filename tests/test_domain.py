# -*- coding: utf-8 -*-
"""Veil domain entity test cases."""
import pytest

from veil_api_client.api_objects.domain import (DomainConfiguration,
                                                DomainRemoteConnectionConfiguration,
                                                DomainTcpUsb,
                                                DomainUpdateConfiguration)


pytestmark = [pytest.mark.domain]


class TestDomainConfigurations:
    """VeilDomain configuration test cases."""

    def test_domain_tcp_usb_init(self):
        """Basic DomainTcpUsb.__init__ test."""
        tcp_usb_configuration = DomainTcpUsb('127.0.0.1', 5431)
        assert tcp_usb_configuration.host == '127.0.0.1'
        assert tcp_usb_configuration.service == 5431

    def test_domain_configuration_init_1(self, known_uid):
        """Basic DomainConfiguration.__init__ test."""
        domain_configuration = DomainConfiguration(verbose_name='test-domain-1',
                                                   parent=known_uid)
        assert domain_configuration.count == 1
        assert domain_configuration.thin
        assert domain_configuration.verbose_name == 'test-domain-1'
        assert domain_configuration.parent == known_uid

    def test_domain_configuration_init_2(self, known_uid):
        """Basic DomainConfiguration.__init__ test."""
        try:
            DomainConfiguration(verbose_name='test-domain-1',
                                parent=known_uid,
                                node=known_uid,
                                resource_pool=known_uid)
        except ValueError:
            assert True
        else:
            raise AssertionError()

    def test_domain_configuration_init_3(self):
        """Basic DomainConfiguration.__init__ test."""
        try:
            DomainConfiguration(verbose_name='test-domain-1', parent='parent')
        except TypeError:
            assert True
        else:
            raise AssertionError()

    def test_domain_update_configuration_init(self):
        """Basic DomainUpdateConfiguration.__init__ test."""
        domain_update_configuration = DomainUpdateConfiguration(verbose_name='test-domain-1',
                                                                description='desc')
        assert domain_update_configuration.verbose_name == 'test-domain-1'
        assert domain_update_configuration.description == 'desc'

    def test_domain_remote_connection_configuration_init_1(self):
        """Basic DomainRemoteConnectionConfiguration.__init__ test."""
        url = '/no-vnc/vnc.html?host=192.168.11.102&password=SPkKastQjQD&path=websockify?token=bebdc920-ac17'  # noqa: E501
        drc = DomainRemoteConnectionConfiguration(connection_url=url,
                                                  connection_type='VNC')
        assert drc.host == '192.168.11.102'
        assert drc.password == 'SPkKastQjQD'
        assert drc.token == 'bebdc920-ac17'
        assert drc.valid

    def test_domain_remote_connection_configuration_init_2(self):
        """Basic DomainRemoteConnectionConfiguration.__init__ test."""
        url = '/spice-html5/spice_auto.html?host=192.168.11.102&password=SPkKastQjQ&path=websockify?token=2385c0a9-940f'  # noqa: E501
        drc = DomainRemoteConnectionConfiguration(connection_url=url,
                                                  connection_type='SPICE')
        assert drc.host == '192.168.11.102'
        assert drc.password == 'SPkKastQjQ'
        assert drc.token == '2385c0a9-940f'
        assert drc.valid

    def test_domain_remote_connection_configuration_init_3(self):
        """Basic DomainRemoteConnectionConfiguration.__init__ test."""
        url = '/spice-html5/spice_auto.html'
        drc = DomainRemoteConnectionConfiguration(connection_url=url,
                                                  connection_type='SPICE')
        assert not drc.host
        assert not drc.password
        assert not drc.token
        assert not drc.valid

    def test_domain_remote_connection_configuration_init_4(self):
        """Basic DomainRemoteConnectionConfiguration.__init__ test."""
        url = '/spice-html5/spice_auto.html?host=192.168.11.102&password=SPkKastQjQ&path=websockify'  # noqa: E501
        drc = DomainRemoteConnectionConfiguration(connection_url=url,
                                                  connection_type='SPICE')
        assert drc.host == '192.168.11.102'
        assert drc.password == 'SPkKastQjQ'
        assert not drc.token
        assert not drc.valid

    def test_domain_remote_connection_configuration_init_5(self):
        """Basic DomainRemoteConnectionConfiguration.__init__ test."""
        url = '/spice-html5/spice_auto.html?password=SPkKastQjQ&path=websockify'
        drc = DomainRemoteConnectionConfiguration(connection_url=url,
                                                  connection_type='SPICE')
        assert not drc.host == '192.168.11.102'
        assert drc.password == 'SPkKastQjQ'
        assert not drc.token
        assert not drc.valid
