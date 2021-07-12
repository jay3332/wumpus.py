from __future__ import annotations

from abc import ABC
from functools import wraps
from inspect import getmembers
from typing import Dict, Iterable, Tuple, Type, TypeVar


T = TypeVar('T', bound='Bitfield')


def bit(value: int, /):
    def decorator(function, /, *, is_bit_alias: bool = False):
        @property
        @wraps(function)
        def wrapper(self: Bitfield, /):
            return self._has(value)

        @wrapper.setter
        def wrapper(self: Bitfield, toggle: bool, /):
            self._set(toggle)

        wrapper.fget.__is_bit_alias__ = is_bit_alias
        wrapper.fget.__value__ = value
        return wrapper
    return decorator
    

def bit_alias(value: int):
    def decorator(function):
        return bit(value)(function, is_bit_alias=True)

    return decorator


class BitfieldMeta(type):
    @property
    def __mapping__(cls, /) -> Dict[str, int]:
        mapping = {}
        for name, item in getmembers(cls):
            if (
                isinstance(item, property)
                and hasattr(item.fget, '__is_bit_alias__') 
                and not item.fget.__is_bit_alias__
            ):
                mapping[name] = item.fget.__value__

        return mapping

    @property
    def __max_value__(cls, /) -> int:
        buffer = max(cls.__mapping__.values())
        return 2 ** buffer.bit_length() - 1


class Bitfield(metaclass=BitfieldMeta):
    """
    Represents a collection of bits, usually used for 
    storing booleans efficiently.

    Internally, these represent an integer.
    """

    def __init__(self, value: int = None, /):
        self._value: int = value or 0

    def __str__(self, /) -> str:
        return str(self._value)

    def __repr__(self, /) -> str:
        return f'<{self.__class__.__name__} value={self._value}>'

    def __int__(self, /) -> int:
        return self._value

    def __iter__(self, /) -> Iterable[Tuple[int, bool]]:
        for key, value in self.__class__.__mapping__.items():
            yield key, self._has(value)

    def __getitem__(self, key: int, /) -> bool:       
        return self._has(key)

    def __setitem__(self, key: int, toggle: bool, /) -> None:
        self._set(key, toggle)

    def _has(self, other: int, /) -> bool:
        return (self._value & other) == other

    def _set(self, other: int, /, toggle: bool = True) -> int:
        if toggle:
            self._value |= other
        else:
            self._value &= ~other

        return self._value

    @classmethod
    def _calculate(cls, /, **kwargs) -> int:
        mapping = cls.__mapping__        
        buffer = 0

        for name, toggle in kwargs.items():
            if name in mapping:
                if toggle:
                    buffer |= mapping[name]
                else:
                    buffer &= ~mapping[name]
            else:
                raise ValueError(f'{name!r} is not a valid field')        

        return buffer

    @classmethod
    def _from_kwargs(cls: Type[T], /, **kwargs) -> T:
        return cls(cls._calculate(**kwargs))


class InvertedBitfield(Bitfield):
    """
    Base class for inverted bitfields.
    """

    def __init__(self, value: int = None, /):
        self._value: int = value or self.__class__.__max_value__

    def _has(self, other: int, /) -> bool:
        return not super()._has(other)

    def _set(self, other: int, /, toggle: bool = True) -> int:
        return super()._set(other, not toggle)
