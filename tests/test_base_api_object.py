# -*- coding: utf-8 -*-
"""Base api object test cases."""
import uuid

import pytest

from veil_api_client.base.api_object import VeilApiObject, VeilRestPaginator

pytestmark = [pytest.mark.base]


class TestVeilRestPaginator:
    """VeilRestPaginator test cases."""

    def test_init(self):
        """Veil rest paginator init test case."""
        try:
            VeilRestPaginator(name='name', ordering='ordering', limit=10, offset=5)
        except TypeError:
            raise AssertionError()
        else:
            assert True
        try:
            VeilRestPaginator(name=123, ordering='ordering', limit=10, offset=5)
        except TypeError:
            assert True
        else:
            raise AssertionError()

    def test_notnull_attrs(self):
        """Notnull attrs should return only not null arguments."""
        obj = VeilRestPaginator(name='name', ordering='ordering', limit=None, offset=5)
        assert 'name' in obj.notnull_attrs
        assert 'limit' not in obj.notnull_attrs


class TestVeilApiObject:
    """VeilApiObject test cases."""

    @pytest.mark.asyncio
    async def test_init_2(self, veil_cli):
        """Test case with bad api_object_id in init."""
        try:
            VeilApiObject(client=veil_cli,
                          api_object_prefix='domain',
                          api_object_id='badUUID')
        except TypeError as err:
            assert str(err) == 'badUUID is not a uuid string.'
        else:
            raise AssertionError()

    @pytest.mark.asyncio
    async def test_init_3(self, veil_cli):
        """Test case with minimal init attributes."""
        try:
            obj = VeilApiObject(client=veil_cli, api_object_prefix='domain')
        except TypeError:
            raise AssertionError()
        else:
            assert isinstance(obj, VeilApiObject)

    @pytest.mark.asyncio
    async def test_init_4(self, veil_cli):
        """Test case with good api_object_id in init."""
        try:
            obj = VeilApiObject(client=veil_cli, api_object_prefix='domain',
                                api_object_id='eafc39f3-ce6e-4db2-9d4e-1d93babcbe26')
        except TypeError:
            raise AssertionError()
        else:
            assert isinstance(obj, VeilApiObject)
        obj.verbose_name = 'test_verbose'

        assert 'eafc39f3-ce6e-4db2-9d4e-1d93babcbe26 : test_verbose - domain' in obj.__str__()
        assert 'eafc39f3-ce6e-4db2-9d4e-1d93babcbe26 : test_verbose' in obj.__repr__()

    def test_api_object_uuid(self, api_object):
        """Test case for api object uuid property."""
        assert isinstance(api_object.uuid_, uuid.UUID)

    def test_api_object_base_url(self, api_object, server_address):
        """Test case for api object base url property."""
        expected_base_url = 'https://{}/api/domain/'.format(server_address)
        assert api_object.base_url == expected_base_url

    def test_api_object_url_1(self, api_object, server_address):
        """Test case for api object url property."""
        expected_url = 'https://{}/api/domain/{}/'.format(server_address, api_object.uuid_)
        assert api_object.api_object_url == expected_url

    def test_api_object_url_2(self, api_object, server_address):
        """Test case for api object url property without api_object_id."""
        try:
            api_object.api_object_id = None
            api_object.api_object_url
        except AttributeError:
            assert True
        else:
            raise AssertionError()

    def test_api_object_update_public(self, api_object):
        """Test case for api object update_public_attrs method."""
        attrs_dict = {'status': 'CREATING'}
        api_object.update_public_attrs(attrs_dict)
        assert api_object.status == 'CREATING'

    def test_api_object_update_private(self, api_object):
        """Test case for api object update_public_attrs method."""
        attrs_dict = {'_client': 'CREATING'}
        api_object.update_public_attrs(attrs_dict)
        assert api_object._client != 'CREATING'

    def test_api_object_update_property(self, api_object):
        """Test case for api object update_public_attrs method."""
        attrs_dict = {'uuid_': 'CREATING'}
        api_object.update_public_attrs(attrs_dict)
        assert api_object.uuid_ != 'CREATING'

    def test_api_object_update_callable(self, api_object):
        """Test case for api object update_public_attrs method."""
        attrs_dict = {'info': 'CREATING'}
        api_object.update_public_attrs(attrs_dict)
        assert api_object.info != 'CREATING'

    def test_api_object_public_attrs(self, api_object):
        """Test case for api object public_attrs method."""
        pub_attrs = api_object.public_attrs
        assert 'update_public_attrs' not in pub_attrs
        assert 'uuid_' in pub_attrs

    def test_api_object_creating_property(self, api_object):
        """Test case for creating property."""
        api_object.status = 'CREATING'
        assert api_object.creating
        assert not api_object.partial

    def test_api_object_active_property(self, api_object):
        """Test case for active property."""
        api_object.status = 'ACTIVE'
        assert api_object.active
        assert not api_object.creating

    def test_api_object_failed_property(self, api_object):
        """Test case for active property."""
        api_object.status = 'FAILED'
        assert api_object.failed
        assert not api_object.creating

    def test_api_object_deleting_property(self, api_object):
        """Test case for deleting property."""
        api_object.status = 'DELETING'
        assert api_object.deleting
        assert not api_object.creating

    def test_api_object_service_property(self, api_object):
        """Test case for service property."""
        api_object.status = 'SERVICE'
        assert api_object.service
        assert not api_object.creating

    def test_api_object_partial_property(self, api_object):
        """Test case for partial property."""
        api_object.status = 'PARTIAL'
        assert api_object.partial
        assert not api_object.creating

    def test_update_public_attr(self, api_object):
        """Test case for update_public_attr method."""
        attrs_dict = dict(status='SERVICE', not_in_public='secret')
        api_object.update_public_attrs(attrs_dict)
        assert api_object.status == 'SERVICE'
        try:
            api_object.not_in_public
        except AttributeError:
            assert True
        else:
            raise AssertionError

    def test_update_or_set_public_attr(self, api_object):
        """Test case for update_or_set_public_attr method."""
        attrs_dict = dict(status='SERVICE', not_in_init='secret', _private='secret')
        api_object.update_or_set_public_attrs(attrs_dict)
        assert api_object.status == 'SERVICE'
        try:
            assert api_object.not_in_init == 'secret'
        except AttributeError:
            raise AssertionError
        else:
            assert True
        try:
            api_object._private
        except AttributeError:
            assert True
        else:
            raise AssertionError
