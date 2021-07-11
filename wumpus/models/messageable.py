from abc import ABC
from typing import Generic, TypeVar

from ..core.connection import Connection
from .objects import NativeObject

from ..typings import Snowflake


T = TypeVar('T', bound=NativeObject)

__all__ = (
    'Messageable',
)


class Messageable(Generic[T], ABC):
    def __init__(self, connection: Connection, /, id: Snowflake) -> None:
        self._connection: Connection = connection
        self._id: Snowflake = id

    async def send(
        self,
        /,
        content: str = None,
    ) -> Message:
        payload = {}
        if content is not None:
            payload['content'] = content

        return await self._connection.api.channels(self._id).messages.post(payload)
