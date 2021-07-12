from .objects import NativeObject

from ..core.connection import Connection
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
    def content(self, /) -> str:
        return self._content

    def _copy(self, /):
        ...