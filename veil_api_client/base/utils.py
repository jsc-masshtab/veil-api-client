# -*- coding: utf-8 -*-
"""Utilities."""
import functools
import inspect
import re
import typing
from uuid import UUID

try:
    from aiohttp.client_reqrep import ClientResponse
except ImportError:  # pragma: no cover
    ClientResponse = None

from .api_response import VeilApiResponse


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
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))  # noqa: E501

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


class NullableBoolType(BoolType):
    """Descriptor for bool checking."""

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type."""
        if isinstance(value, self.value_type) or value is None:
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))  # noqa: E501


class IntType(TypeChecker):
    """Descriptor for int checking."""

    def __init__(self, name):
        """Use 'int' for TypeChecker value_type."""
        super().__init__(name, int)


class SetType(TypeChecker):
    """Descriptor for set checking."""

    def __init__(self, name):
        """Use 'set' for TypeChecker value_type."""
        super().__init__(name, set)


class NullableSetType(SetType):
    """Descriptor for set checking."""

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type."""
        if isinstance(value, self.value_type) or value is None:
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))  # noqa: E501


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
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))  # noqa: E501


class NullableStringType(StringType):
    """Descriptor for nullable string checking."""

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type."""
        if isinstance(value, self.value_type) or value is None:
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))  # noqa: E501


class NullableIntType(IntType):
    """Descriptor for nullable int checking."""

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type."""
        if isinstance(value, self.value_type) or value is None:
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))  # noqa: E501


class VeilJwtTokenType(StringType):
    """JWT Token is a string begins with 'jwt '."""

    __TOKEN_PREFIX = re.compile('jwt ', re.I)

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type and starts with 'jwt ' or 'JWT '."""  # noqa: E501
        if isinstance(value, self.value_type) and self.__TOKEN_PREFIX.match(value):
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a proper VeiL jwt-token.'.format(val=value))


class VeilSlugType(StringType):
    """Descriptor for VeiL slug field."""

    __SLUG_PREFIX = re.compile('^[-a-zA-Z0-9_]+$', re.I)

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type and looks like veil slug pattern."""  # noqa: E501
        if isinstance(value, self.value_type) and self.__SLUG_PREFIX.match(value) and len(value) <= 60:  # noqa: E501
            instance.__dict__[self.name] = value
        else:
            raise TypeError('{val} is not a proper VeiL slug.'.format(val=value))


class HexColorType(NullableStringType):
    """Descriptor for hex-color str checking."""

    __COLOR_PREFIX = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', re.I)

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type and looks like hex-color."""  # noqa: E501
        if isinstance(value, self.value_type) and self.__COLOR_PREFIX.match(value) and len(value) <= 7:  # noqa: E501
            instance.__dict__[self.name] = value
        elif not value:
            instance.__dict__[self.name] = '#c0ffee'
        else:
            raise TypeError('{val} is not a proper hex-color str.'.format(val=value))


class UuidStringType(NullableStringType):
    """Check that string is a uuid-representation."""

    def __set__(self, instance, value):
        """Check that attribute value can be converted to UUID."""
        try:
            if value and isinstance(value, UUID):
                value = str(value)
            elif value:
                UUID(value)

        except (ValueError, AttributeError):
            raise TypeError('{val} is not a uuid string.'.format(val=value))
        else:
            super().__set__(instance, value)


class NullableUuidStringType(UuidStringType):
    """Descriptor for nullable uuid checking."""

    def __set__(self, instance, value):
        """Check that value is None or can be converted to UUID."""
        if value is None:
            pass
        super().__set__(instance, value)


class VeilUrlStringType(StringType):
    """Check that string is a valid HTTP-address."""

    regex = re.compile(
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...  # noqa: E501
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
                    raise TypeError('{arg} is not a proper {arg_type}.'.format(arg=arg_value, arg_type=arg_annotation))  # noqa: E501

            for kwarg in kwargs:
                kwarg_annotation = annotations.get(kwarg)
                kwarg_value = kwargs[kwarg]
                if hasattr(kwarg_annotation, '__origin__') and kwarg_annotation.__origin__ is typing.Union:  # noqa: E501
                    continue
                if kwarg_annotation and kwarg_value and not isinstance(kwarg_value, kwarg_annotation):  # noqa: E501
                    raise TypeError(
                        '{kwarg} is not a proper {arg_type}.'.format(kwarg=kwarg, arg_type=kwarg_annotation))  # noqa: E501

        return func(*args, **kwargs)
    return wrapper


def veil_api_response(func) -> 'VeilApiResponse':
    """Make VeilApiResponse from aiohttp.response."""

    @functools.wraps(func)
    async def wrapper(client,
                      api_object,
                      *args, **kwargs):
        resp = await func(client, *args, **kwargs)
        if isinstance(resp, dict):
            # Make response object instance
            return VeilApiResponse(status_code=resp['status_code'],
                                   data=resp['data'],
                                   headers=resp['headers'],
                                   api_object=api_object)
        return resp  # pragma: no cover
    return wrapper


class VeilConfiguration:
    """Abstract VeiL configuration."""

    @property
    def notnull_attrs(self) -> dict:
        """Return only attributes with values."""
        return {attr: self.__dict__[attr] for attr in self.__dict__ if self.__dict__[attr] is not None}  # noqa: E501


class VeilEntityConfiguration(VeilConfiguration):
    """VeiL Entity struct.

    Attributes:
        entity_uuid: VeiL ECP entity uuid.
        entity_class: VeiL ECP entity type in single form (domain, datapool, etc).
    """

    entity_uuid = UuidStringType('entity_uuid')
    entity_class = StringType('entity_class')

    def __init__(self, entity_uuid: str, entity_class: str, entity_name: typing.Optional[str] = None, **_):  # noqa: E501
        """Please see help(VeilEntityConfiguration) for more info."""
        self.entity_uuid = entity_uuid
        self.entity_class = entity_class
        self.entity_name = entity_name

    def __repr__(self):
        """Original repr and additional info."""
        original_repr = super().__repr__()
        return '{} : {} : {}: {}'.format(original_repr, self.entity_uuid, self.entity_class, self.entity_name)  # noqa: E501

    def __str__(self):
        """Just verbose_name."""
        return '{}'.format(self.entity_class)


class VeilEntityConfigurationType(TypeChecker):
    """Descriptor for VeilEntityConfiguration checking."""

    def __init__(self, name):
        """Set attribute name and checking value type."""
        super().__init__(name, list)

    def __set__(self, instance, value):
        """Check that attribute value type equals value_type."""
        if isinstance(value, self.value_type):
            instance.__dict__[self.name] = [VeilEntityConfiguration(**val) for val in value]
        elif not value:
            instance.__dict__[self.name] = None
        else:
            raise TypeError('{val} is not a {val_type}'.format(val=value, val_type=self.value_type))  # noqa: E501


class VeilRetryConfiguration(VeilConfiguration):
    """Retry configuration class for veil api client.

    Attributes:
        num_of_attempts: num of retry attempts.
        timeout: base try timeout time (with exponential grow).
        max_timeout: max timeout between tries.
        timeout_increase_step: timeout increase step.
        status_codes: collection of response status codes witch must be repeated.
        exceptions: collection of aiohttp exceptions witch must be repeated.
    """

    num_of_attempts = IntType('num_of_attempts')
    timeout = IntType('timeout')
    max_timeout = IntType('max_timeout')
    timeout_increase_step = IntType('timeout_increase_step')
    status_codes = NullableSetType('status_codes')
    exceptions = NullableSetType('exceptions')

    def __init__(self,
                 num_of_attempts: int = 0,
                 timeout: int = 1,
                 max_timeout: int = 30,
                 timeout_increase_step: int = 2,
                 status_codes: typing.Optional[set] = None,
                 exceptions: typing.Optional[set] = None
                 ) -> None:
        """Please see help(VeilRetryConfiguration) for more info."""
        self.num_of_attempts = num_of_attempts
        self.timeout = timeout
        self.max_timeout = max_timeout
        self.timeout_increase_step = timeout_increase_step
        self.status_codes = status_codes
        self.exceptions = exceptions
