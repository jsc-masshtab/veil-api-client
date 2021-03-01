# -*- coding: utf-8 -*-
"""Descriptor test cases."""
from uuid import uuid4

import pytest

from veil_api_client.base import utils

pytestmark = [pytest.mark.base]


class TestAttributeDescriptors:
    """Class attribute descriptors tests."""

    @classmethod
    def setup_class(cls):
        """Test mock values."""

        class TemporaryClass:
            tuple_type = utils.TypeChecker('unknown_type', tuple)
            str_type = utils.StringType('str_type')
            bool_type = utils.BoolType('bool_type')
            nullable_bool_type = utils.NullableBoolType('nullable_bool_type')
            nullable_str_type = utils.NullableStringType('nullable_str_type')
            nullable_set_type = utils.NullableSetType('nullable_set_type')
            int_type = utils.IntType('int_type')
            nullable_int_type = utils.NullableIntType('nullable_int_type')
            dict_type = utils.DictType('dict_type')
            nullable_dict_type = utils.NullableDictType('nullable_dict_type')
            veil_jwt_token_type = utils.VeilJwtTokenType('veil_jwt_token_type')
            veil_url_string_type = utils.VeilUrlStringType('veil_url_string_type')
            uuid_string_type = utils.UuidStringType('uuid_string_type')
            nullable_uuid_string_type = utils.NullableUuidStringType('nullable_uuid_string_type')  # noqa: E501
            veil_slug_type = utils.VeilSlugType('veil_slug_type')
            hex_color_type = utils.HexColorType('hex_color_type')
            entity_configuration_type = utils.VeilEntityConfigurationType('entity_configuration_type')  # noqa: E501

            @utils.argument_type_checker_decorator
            def annotated(self, val: str = None):
                pass

        cls._instance_class_being_tested = TemporaryClass()

    def assert_value(self, class_argument: str, good_value, bad_value):
        """Check good and bad value setting."""
        try:
            setattr(self._instance_class_being_tested, class_argument, good_value)
        except TypeError:
            raise AssertionError()
        else:
            assert getattr(self._instance_class_being_tested, class_argument) == good_value  # noqa: E501
        try:
            setattr(self._instance_class_being_tested, class_argument, bad_value)
        except TypeError:
            assert True
        else:
            raise AssertionError()

    def test_string_type_checker(self):
        """String type descriptor test case."""
        self.assert_value(class_argument='str_type',
                          good_value='string',
                          bad_value=123)

    def test_tuple_type_checker(self):
        """Tuple type descriptor test case."""
        self.assert_value(class_argument='tuple_type',
                          good_value=('k', 'v'),
                          bad_value=['k', 'v'])

    def test_bool_type_checker(self):
        """Bool type descriptor test case."""
        self.assert_value(class_argument='bool_type',
                          good_value=True,
                          bad_value='null')

    def test_nullable_str_type_checker(self):
        """Nullable str type descriptor test case."""
        self.assert_value(class_argument='nullable_str_type',
                          good_value=None,
                          bad_value=1)

    def test_int_type_checker(self):
        """Int type descriptor test case."""
        self.assert_value(class_argument='int_type',
                          good_value=1,
                          bad_value='1')

    def test_nullable_int_type_checker(self):
        """Int type descriptor test case."""
        self.assert_value(class_argument='nullable_int_type',
                          good_value=None,
                          bad_value='1')

    def test_dict_type_checker(self):
        """Dict type descriptor test case."""
        self.assert_value(class_argument='dict_type',
                          good_value={'k': 'v'},
                          bad_value='1')

    def test_nullable_dict_type_checker(self):
        """Nullable dict type descriptor test case."""
        self.assert_value(class_argument='nullable_dict_type',
                          good_value=None,
                          bad_value='1')

    def test_veil_jwt_token_type_checker(self):
        """Veil jwt token type checker."""
        self.assert_value(class_argument='veil_jwt_token_type',
                          good_value='jwt AsDaAS1123',
                          bad_value='AsDaAS1123')

    def test_veil_url_string_type_checker_1(self):
        """Veil url string type checker."""
        self.assert_value(class_argument='veil_url_string_type',
                          good_value='127.0.0.1',
                          bad_value='https://127.0.0.1')

    def test_veil_url_string_type_checker_2(self):
        """Another veil url string type checker."""
        self.assert_value(class_argument='veil_url_string_type',
                          good_value='ya.ru:8888',
                          bad_value='https://ya.ru')

    def test_uuid_string_type_checker(self):
        """Uuid string type checker."""
        self.assert_value(class_argument='uuid_string_type',
                          good_value='eafc39f3-ce6e-4db2-9d4e-1d93babcbe26',
                          bad_value='eafc39f3-ce6e-4db2-9d4e-1d93babcbe2')

    def test_nullable_uuid_string_type_checker(self):
        """Nullable uuid string type checker."""
        self.assert_value(class_argument='nullable_uuid_string_type',
                          good_value=None,
                          bad_value=1)

    def test_method_annotated_argument(self):
        """Decorator argument_type_checker."""
        try:
            self._instance_class_being_tested.annotated(val='1')
        except TypeError:
            raise AssertionError()
        else:
            assert True
        try:
            self._instance_class_being_tested.annotated('1')
        except TypeError:
            raise AssertionError()
        else:
            assert True
        try:
            self._instance_class_being_tested.annotated(val=1)
        except TypeError:
            assert True
        else:
            raise AssertionError()
        try:
            self._instance_class_being_tested.annotated(1)
        except TypeError:
            assert True
        else:
            raise AssertionError()

    def test_nullable_bool_type_checker(self):
        """Nullable bool type descriptor test case."""
        self.assert_value(class_argument='nullable_bool_type',
                          good_value=None,
                          bad_value='1')

    def test_nullable_set_type_checker(self):
        """Nullable set type descriptor test case."""
        self.assert_value(class_argument='nullable_set_type',
                          good_value=None,
                          bad_value='1')

    def test_veil_slug_type(self):
        """Veil slug type descriptor test case."""
        self.assert_value(class_argument='veil_slug_type',
                          good_value='slug',
                          bad_value='slug!')

    def test_hex_color_type(self):
        """Hex color type descriptor test case."""
        self.assert_value(class_argument='hex_color_type',
                          good_value='#a377e6',
                          bad_value='red')

    def test_uuid_string_type_checker_2(self):
        """Uuid string type checker."""
        test_val = uuid4()
        try:
            setattr(self._instance_class_being_tested, 'uuid_string_type', test_val)  # noqa: B010, E501
        except TypeError:
            raise AssertionError()
        else:
            assert getattr(self._instance_class_being_tested, 'uuid_string_type') == str(test_val)  # noqa: B009, E501

    def test_hex_color_type_2(self):
        """Hex color type descriptor test case."""
        try:
            setattr(self._instance_class_being_tested, 'hex_color_type', None)  # noqa: B010
        except TypeError:
            raise AssertionError()
        else:
            assert getattr(self._instance_class_being_tested, 'hex_color_type') == '#c0ffee'  # noqa: B009, E501

    def test_veil_entity_configuration_type(self):
        """Veil entity configuration type test case."""
        try:
            id_ = str(uuid4())
            setattr(self._instance_class_being_tested, 'entity_configuration_type', [{'entity_uuid': id_,  # noqa: B010, E501
                                                                                      'entity_class': 'test_entity'}  # noqa: E501
                                                                                     ])
        except TypeError:
            raise AssertionError()
        else:
            val = getattr(self._instance_class_being_tested, 'entity_configuration_type')  # noqa: B009, E501
            assert isinstance(val[0], utils.VeilEntityConfiguration)
        try:
            setattr(self._instance_class_being_tested, 'entity_configuration_type', None)  # noqa: B010, E501
        except TypeError:
            raise AssertionError()
        else:
            assert True
        try:
            id_ = str(uuid4())
            setattr(self._instance_class_being_tested, 'entity_configuration_type', {'entity_uuid': id_,  # noqa: B010, E501
                                                                                     'entity_class': 'test_entity'})  # noqa: E501
        except TypeError:
            assert True
        else:
            raise AssertionError()


class TestVeilEntityConfiguration:
    """Entity configuration test cases."""

    def test_init(self):
        """Init tests."""
        id_ = str(uuid4())
        cl = utils.VeilEntityConfiguration(entity_uuid=id_, entity_class='domain')
        assert True
        repr_val = '{} : domain'.format(id_)
        assert repr_val in cl.__repr__()
        assert 'domain' == cl.__str__()
