# -*- coding: utf-8 -*-
"""Descriptor test cases."""
import pytest

from veil_api_client.base import descriptors

pytestmark = [pytest.mark.base]


class TestAttributeDescriptors:
    """Class attribute descriptors tests."""

    @classmethod
    def setup_class(cls):
        """Test mock values."""

        class TemporaryClass:
            tuple_type = descriptors.TypeChecker('unknown_type', tuple)
            str_type = descriptors.StringType('str_type')
            bool_type = descriptors.BoolType('bool_type')
            nullable_str_type = descriptors.NullableStringType('nullable_str_type')
            int_type = descriptors.IntType('int_type')
            nullable_int_type = descriptors.NullableIntType('nullable_int_type')
            dict_type = descriptors.DictType('dict_type')
            nullable_dict_type = descriptors.NullableDictType('nullable_dict_type')
            veil_jwt_token_type = descriptors.VeilJwtTokenType('veil_jwt_token_type')
            veil_url_string_type = descriptors.VeilUrlStringType('veil_url_string_type')
            uuid_string_type = descriptors.UuidStringType('uuid_string_type')

            @descriptors.argument_type_checker_decorator
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
            assert getattr(self._instance_class_being_tested, class_argument, good_value) == good_value
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
