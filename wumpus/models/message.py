from typing import Union

from .emoji import PartialEmoji
from .objects import NativeObject

from ..core.connection import Connection
from ..core.http import Router

from ..typings.payloads import MessagePayload


class Message(NativeObject):
    def __init__(self, connection: Connection, /, data: MessagePayload):
        self._connection: Connection = connection
        self._load_data(data)
        super().__init__()

    def _load_data(self, data: MessagePayload, /) -> None:
        super()._put_snowflake(data['id'])

        self._content: str = data.get('content', '')

    @property
    def _api(self, /) -> Router:
        return self._connection.api.channels(self._channel_id).messages(self.id)

    @property
    def content(self, /) -> str:
        return self._content

    def _copy(self, /):
        ...

    async def delete(self, /, *, reason: str = None) -> None:
        return await self._api.delete(reason=reason)

    async def react(self, /, emoji: Union[str, PartialEmoji]) -> None:
        if isinstance(emoji, str):
            emoji = PartialEmoji.parse(emoji)
        return await self._api.reactions(emoji._to_route()).me.put()

    async def unreact(self, /, emoji: Union[str, PartialEmoji]) -> None:
        return await self._api.reactions(emoji._to_route()).me.delete()
