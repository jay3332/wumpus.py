from .asset import Asset
from .objects import NativeObject
from .connection import Connection
from ..typings.payloads import PartialUserPayload, UserPayload

from typing import Literal

__all__ = (
    'PartialUser',
)

UserFormat = Literal['m', 'n', 't']


class PartialUser(NativeObject):
    __slots__ = ('_name', '_discriminator', '_avatar') + NativeObject.__slots__

    def __init__(self, connection: Connection, data: PartialUserPayload) -> None:
        self._connection: Connection = connection
        self._load_data(data)
        super().__init__()

    def _load_data(self, data: PartialUserPayload) -> None:
        self._last_received_data = data
        self._put_snowflake(data['id'])

        self._name: str = data['username']
        self._discriminator: str = data['discriminator']

        _avatar_hash = data['avatar']
        _avatar_animated = _avatar_hash.startswith('a_')

        self._avatar: Asset = Asset(
            self._connection,
            url=f'avatars/{self.id}/{_avatar_hash}',
            animated=_avatar_animated,
            hash=_avatar_animated
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def discriminator(self) -> str:
        return self._discriminator

    @property
    def avatar(self) -> Asset:
        return self._avatar

    @property
    def tag(self) -> str:
        return f'{self.name}#{self.discriminator}'

    @property
    def mention(self) -> str:
        return f'<@{self.id}>'

    def __str__(self) -> str:
        return self.tag

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} name={self.name!r} discriminator={self.discriminator!r} id={self.id}>'

    def __format__(self, format: UserFormat) -> str:
        format = format.lower()

        if not format or format == 't':
            return str(self)

        if format == 'm':
            return self.mention
        elif format == 'n':
            return self.name

        raise ValueError(f'invalid format for User {format!r}')
