from typing import Any, Dict, Tuple

from .connection import Connection
from ..typings import JSON
from ..typings.payloads import (
    ReadyEventPayload
)


__all__ = (
    'EventEmitter',
)


class _BaseEventEmitter:
    def __init__(self, connection: Connection, /) -> None:
        self._connection: Connection = connection

    def handle(self, event: str, /, data: JSON) -> None:
        event = event.lower()

        if hasattr(self, event):
            coro = getattr(self, event)(data)
            self._connection.loop.create_task(coro)


class EventEmitter(_BaseEventEmitter):
    # TODO: Make JSON typehint TypedDicts

    async def ready(self, data: ReadyEventPayload, /) -> None:
        self._connection.patch_current_user(data['user'])

    async def message_create(self, data: JSON, /) -> None:
        ...
