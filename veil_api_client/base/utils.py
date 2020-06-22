# -*- coding: utf-8 -*-
"""Utilities."""
import re
from uuid import UUID


class TypeChecker:
    """Descriptor for type checking."""

    def __init__(self, name, value_type):
        """Set attribute name and checking value type."""
        self.name = name
        self.value_type = value_type

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type."""
        if isinstance(value, self.value_type):
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))

    def __get__(self, instance, class_):
        """Return attribute value."""
        return instance.__dict__[self.name]


class StringType(TypeChecker):
    """Descriptor for string checking."""

    def __init__(self, name):
        """Use 'str' for TypeChecker value_type."""
        super().__init__(name, str)


class BoolType(TypeChecker):
    """Descriptor for bool checking."""

    def __init__(self, name):
        """Use 'bool' for TypeChecker value_type."""
        super().__init__(name, bool)


class DictType(TypeChecker):
    """Descriptor for dict checking."""

    def __init__(self, name):
        """Use 'dict' for TypeChecker value_type."""
        super().__init__(name, dict)


class NullableDictType(DictType):
    """Descriptor for dict checking."""

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type."""
        if isinstance(value, self.value_type) or value is None:
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))


class NullableStringType(StringType):
    """Descriptor for nullable string checking."""

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type."""
        if isinstance(value, self.value_type) or value is None:
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))


class VeilJwtTokenType(StringType):
    """JWT Token is a string begins with 'jwt '."""

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type and starts with 'jwt '."""
        if isinstance(value, self.value_type) and value.startswith('jwt '):
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a proper VeiL jwt-token.'.format(val=value))


class UuidStringType(NullableStringType):
    """Check that string is a uuid-representation."""

    def __set__(self, instance, value):
        """Check that attribute value can be converted to UUID."""
        try:
            if value:
                UUID(value)
        except ValueError:
            raise TypeError('{val} is not a uuid string.'.format(val=value))
        else:
            super().__set__(instance, value)


class VeilUrlStringType(StringType):
    """Check that string is a valid HTTP-address."""

    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    def __set__(self, instance, value):
        """Check that value is expected http-url."""
        if isinstance(value, self.value_type) and self.regex.match(value):
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a proper VeiL server url.'.format(val=value))
