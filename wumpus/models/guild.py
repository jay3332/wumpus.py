from typing import TypeVar

from .objects import NativeObject

from ..core.connection import Connection
from ..typings.payloads import GuildPayload


T = TypeVar('T', bound='Guild')

__all__ = (
    'Guild',
)


class Guild(NativeObject):
    __slots__ = (
        '_name',
    ) + NativeObject.__slots__

    def __init__(self, connection: Connection, /, data: GuildPayload) -> None:
        self._connection: Connection = connection
        self._last_received_data: GuildPayload = {}
        self._load_data(data)
        super().__init__()

    def _load_data(self, data: GuildPayload) -> None:
        self._last_received_data |= data
        self._put_snowflake(data['id'])

        self._name: str = data['name']

    def _copy(self: T) -> T:
        return self.__class__(self._connection, self._last_received_data)
