from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, NamedTuple, Optional, TypeVar, Type, overload
from datetime import datetime, timezone

from ..typings.core import TimestampStyle, Snowflake


DISCORD_EPOCH: int = 1420070400000


T = TypeVar('T', bound='Object')
DT = TypeVar('DT', bound='Timestamp')


__all__ = (
    'Timestamp',
    'deconstruct_snowflake',
    'Object',
    'NativeObject'
)

_SNOWFLAKE_GEN_INCREMENT = 0


class Timestamp(datetime):
    __slots__ = datetime.__slots__

    @overload
    def __new__(
        cls: Type[DT],
        /,
        year: int,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        tzinfo: timezone = timezone.utc,
        *,
        fold: int = 0
    ) -> DT:
        ...

    def __new__(cls: Type[DT], /, *args, **kwargs) -> DT:
        return super().__new__(*args, **kwargs)

    def __format__(self, style: TimestampStyle, /) -> str:
        if not style:
            return f'<t:{int(self.timestamp())}>'
        
        return f'<t:{int(self.timestamp())}:{style}>'

    @classmethod
    def utcfromtimestamp(cls: Type[DT], timestamp: float) -> DT:
        naive = super().utcfromtimestamp(timestamp)
        return naive.replace(tzinfo=timezone.utc)

    @classmethod
    def from_datetime(cls: Type[DT], dt: datetime) -> DT:
        return cls.utcfromtimestamp(dt.timestamp())

    def to_datetime(self, /) -> datetime:
        args = (
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
            self.tzinfo
        )
        return datetime(*args, fold=self.fold)

    def to_snowflake(
        self,
        /, 
        *,
        worker_id: int = 1, 
        process_id: int = 0,
        increment: int = None
    ) -> Snowflake:
        if increment is None:
            incr = _SNOWFLAKE_GEN_INCREMENT
        else:
            incr = increment
        
        buffer = ((self.timestamp() * 1000) - DISCORD_EPOCH) 
        buffer = (buffer << 5) | worker_id
        buffer = (buffer << 5) | process_id
        buffer = (buffer << 12) | incr

        if increment is None:
            if incr < 4095:
                _SNOWFLAKE_GEN_INCREMENT += 1
            else:
                _SNOWFLAKE_GEN_INCREMENT = 0

        return buffer


class _DeconstructedSnowflake(NamedTuple):
    id: Snowflake
    created_at: Timestamp
    worker_id: int
    process_id: int
    increment: int


def deconstruct_snowflake(snowflake: int) -> _DeconstructedSnowflake:
    buffer = snowflake
    increment = buffer & ((1 << 12) - 1)
    buffer >>= 12
    process = buffer & ((1 << 5) - 1)
    buffer >>= 5
    worker = buffer & ((1 << 5) - 1)
    buffer >>= 5
    timestamp = (buffer + DISCORD_EPOCH) / 1000

    return _DeconstructedSnowflake(
        snowflake,
        Timestamp.utcfromtimestamp(timestamp),
        worker, process, increment
    )


class Object:
    def __init__(self, id: Snowflake = None, /) -> None:
        if id is not None:
            self.__id: Snowflake = id
            self.__dc: _DeconstructedSnowflake = None

    def __deconstruct(self, /) -> None:
        if self.__dc is None:
            self.__dc = deconstruct_snowflake(self.id)
        
    @property
    def id(self, /) -> Snowflake:
        return self.__id

    @property
    def created_at(self, /) -> Timestamp:
        self.__deconstruct()
        return self.__dc.created_at

    @property
    def deconstructed(self, /) -> _DeconstructedSnowflake:
        self.__deconstruct()
        return self.__dc

    def __eq__(self: T, other: T, /) -> bool:
        return self.id == other.id and isinstance(other, self.__class__)

    def __ne__(self: T, other: T, /) -> bool:
        return not self.__eq__(other)

    def __int__(self, /) -> int:
        return self.id

    def __repr__(self, /) -> str:
        return f'<{self.__class__.__name__} id={self.id}>'


class NativeObject(Object, ABC):
    __slots__ = ('__object_cached__', '_connection', '_last_received_data', '__id', '__dc')

    def __init__(self):
        super().__init__()
        self.__object_cached__: bool = True

    def _put_snowflake(self, snowflake: Snowflake) -> None:
        # This data is usually received later
        Object.__init__(self, snowflake)

    @abstractmethod
    def _load_data(self, data: Any, /) -> None:
        raise NotImplementedError

    @abstractmethod
    def _copy(self: T) -> T:
        raise NotImplementedError

    def _copy_and_patch(self: T, data: Any, /) -> T:
        old = self._copy()
        old.__object_cached__ = False
        self._load_data(data)
        return old

    def __copy__(self: T) -> T:
        return self._copy()
