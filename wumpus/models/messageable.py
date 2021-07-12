from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Iterable, overload

from .message import Message
from .objects import NativeObject

from ..core.builder import MessageBuilder

if TYPE_CHECKING:
    from .embed import Embed


__all__ = (
    'Messageable',
)


class Messageable(NativeObject, ABC):
    if TYPE_CHECKING:
        # TODO: Maybe overload embed and file separately

        @overload
        async def send(
            self, 
            /, 
            content: str = None,
            *,
            code: str = None,
            tts: bool = False,
            embed: Embed = None,
            embeds: Iterable[Embed] = None,
            # file: File = None,
            # files: Iterable[File] = None, 
            # reference: Message = None,
            # allowed_mentions: AllowedMentions = None,
            # components: Components = None
        ):
            ...

    @property
    def _messageable_id(self, /) -> int:
        # Primarily here for users
        return self.id

    async def send(self, /, content: str = None, **options) -> Message:
        options |= {'content': content, 'channel_id': self._messageable_id}
        builder = MessageBuilder(self._connection, **options)
        return await builder.send()
