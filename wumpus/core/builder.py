from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable

from .connection import Connection
from ..models.message import Message
from ..typings import JSON


class BaseMessageBuilder(ABC):
    def __init__(
        self,
        connection: Connection,
        /,
        *,
        content: str = None,
        **options
    ) -> None:
        self._connection: Connection = connection
        self._options: Dict[str, Any] = options

        if content is not None:
            self._options['content'] = content
        
        self._extra: Iterable[Any] = self._options.pop('extra', ())
        self._payload: JSON = {}
        self.build()

    def _resolve_content(self, /) -> None:
        content = self._options.get('content') or ''

        if not len(content):
            self._payload['content'] = ''
            return

        code = self._options.get('code')
        if code is not None:
            if code is True:
                content = '```' + content + '```'
            else:
                content = '```' + code + '\n' + content + '```'

        self._payload['content'] = content

    def _resolve_other(self, /) -> None:
        ...

    def build(self, /) -> None:
        self._resolve_content()
        self._resolve_other()

    @abstractmethod
    async def send(self, /) -> Any:
        raise NotImplementedError

    
class MessageBuilder(BaseMessageBuilder):
    def __init__(
        self,
        connection: Connection,
        /,
        *,
        content: str = None,
        **options
    ) -> None:
        self._channel_id: int = options.pop('channel_id', None)
        super().__init__(connection, content=content, **options)

    def _resolve_other(self, /) -> None:
        if 'tts' in self._options: 
            self._payload['tts'] = self._options['tts']

    async def send(self, /) -> Message:
        route = self._connection.api.channels(self._channel_id).messages
        data = await route.post(self._payload)

        # TODO: MessageManager to store this in cache
        return Message(self._connection, data)
