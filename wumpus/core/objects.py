from __future__ import annotations

from typing import NamedTuple, Optional, TypeVar, Type, overload
from datetime import datetime, timezone

from ..typings import TimestampStyle


DISCORD_EPOCH: int = 1420070400000


DT = TypeVar('DT', bound='Timestamp')


__all__ = (
    'Timestamp',
    'deconstruct_snowflake'
)


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



class _DeconstructedSnowflake(NamedTuple):
    id: int
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
    timestamp = (buffer + 1420070400000) / 1000

    return _DeconstructedSnowflake(
        snowflake,
        Timestamp.utcfromtimestamp(timestamp),
        worker, process, increment
    )


class Object:
    def __init__(self, id: int, /) -> None:
        self.__id: int = id
        self.__dc: _DeconstructedSnowflake = None

    def __deconstruct(self, /) -> None:
        if self.__dc is None:
            self.__dc = deconstruct_snowflake(self.id)
        
    @property
    def id(self, /) -> int:
        return self.__id

    @property
    def created_at(self, /) -> Timestamp:
        self.__deconstruct()
        return self.__dc.created_at

    @property
    def deconstructed(self, /) -> _DeconstructedSnowflake:
        self.__deconstruct()
        return self.__dc
