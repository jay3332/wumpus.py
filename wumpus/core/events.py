from typing import Any, Dict, Tuple

from .connection import Connection
from ..typings import JSON


__all__ = (
    'EventEmitter',
)


class _BaseEventEmitter:
    def __init__(self, connection: Connection, /) -> None:
        self._connection: Connection = connection

    def handle(self, event: str, /, data: JSON) -> None:
        event = event.lower()
        if hasattr(self, event):
            self._connection.loop.create_task(
                getattr(self, event)(data)
            )


class EventEmitter(_BaseEventEmitter):
    # TODO: Make JSON typehint TypedDicts

    async def ready(self, data: JSON, /) -> None:
        ...

    async def message_create(self, data: JSON, /) -> None:
        ...
