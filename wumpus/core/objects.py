from __future__ import annotations

from typing import NamedTuple, Optional, TypeVar, Type, overload
from datetime import datetime, timezone

from ..typings import TimestampStyle


DISCORD_EPOCH: int = 1420070400000


T = TypeVar('T', bound='Snowflake')
DT = TypeVar('DT', bound='Timestamp')


__all__ = (
    'Timestamp',
    'Snowflake',
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
    created_at: Timestamp
    worker_id: int
    process_id: int
    increment: int


def deconstruct_snowflake(snowflake: int) -> _DeconstructedSnowflake:
    increment = snowflake & ((1 << 12) - 1)
    snowflake >>= 12
    process = snowflake & ((1 << 5) - 1)
    snowflake >>= 5
    worker = snowflake & ((1 << 5) - 1)
    snowflake >>= 5
    timestamp = (snowflake + 1420070400000) / 1000

    return _DeconstructedSnowflake(
        Timestamp.utcfromtimestamp(timestamp),
        worker, process, increment
    )



class Snowflake(int):
    def __new__(cls: Type[T], value: int) -> T:
        self = super().__new__(value)

        deconstructed = deconstruct_snowflake(value)
        self.created_at = deconstructed.created_at
        self.process_id = deconstructed.process_id
        self.worker_id = deconstructed.worker_id
        self.increment = deconstructed.increment

        return self

    def __repr__(self) -> str:
        return f'Snowflake({self})'


class Object:
    def __init__(self, id: int, /) -> None:
        if not isinstance(id, Snowflake):
            id = Snowflake(id)

        self.__id: Snowflake = id
        
    @property
    def id(self, /) -> Snowflake:
        return self.__id

    @property
    def created_at(self, /) -> Timestamp:
        return self.__id.created_at
