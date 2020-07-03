# -*- coding: utf-8 -*-
"""Utilities."""
import functools
import inspect
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


class IntType(TypeChecker):
    """Descriptor for int checking."""

    def __init__(self, name):
        """Use 'int' for TypeChecker value_type."""
        super().__init__(name, int)


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


class NullableIntType(IntType):
    """Descriptor for nullable int checking."""

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type."""
        if isinstance(value, self.value_type) or value is None:
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))


class VeilJwtTokenType(StringType):
    """JWT Token is a string begins with 'jwt '."""

    __TOKEN_PREFIX = re.compile('jwt ', re.I)

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type and starts with 'jwt ' or 'JWT '."""
        if isinstance(value, self.value_type) and self.__TOKEN_PREFIX.match(value):
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
        except (ValueError, AttributeError):
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


def argument_type_checker_decorator(func):
    """Compare function argument type annotations with value types."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        arguments = inspect.getfullargspec(func).args
        annotations = func.__annotations__

        if annotations:
            for idx, arg_name in enumerate(arguments):
                arg_annotation = annotations.get(arg_name)
                arg_value = args[idx] if len(args) > idx else None
                if arg_annotation and arg_value and not isinstance(arg_value, arg_annotation):
                    raise TypeError('{arg} is not a proper {arg_type}.'.format(arg=arg_value, arg_type=arg_annotation))

            for kwarg in kwargs:
                kwarg_annotation = annotations.get(kwarg)
                if kwarg_annotation and not isinstance(kwargs[kwarg], kwarg_annotation):
                    raise TypeError(
                        '{kwarg} is not a proper {arg_type}.'.format(kwarg=kwarg, arg_type=kwarg_annotation))

        return func(*args, **kwargs)
    return wrapper
