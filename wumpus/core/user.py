from .asset import Asset
from .objects import NativeObject
from .connection import Connection

from ..utils import _bytes_to_image_data
from ..typings.payloads import PartialUserPayload, UserPayload

from typing import Literal, Optional, Union

__all__ = (
    'PartialUser',
    'ClientUser'
)

UserFormat = Literal['m', 'n', 't']


class PartialUser(NativeObject):
    __slots__ = ('_name', '_discriminator', '_avatar') + NativeObject.__slots__

    _avatar: Asset

    def __init__(self, connection: Connection, /, data: PartialUserPayload) -> None:
        self._connection: Connection = connection
        self._load_data(data)
        super().__init__()

    def _load_data(self, data: PartialUserPayload) -> None:
        self._last_received_data = data
        self._put_snowflake(data['id'])

        self._name: str = data['username']
        self._discriminator: str = data['discriminator']

        try:
            _avatar_hash = data['avatar']
        except KeyError:
            self._avatar = None
            self.__avatar_hash = None
        else:
            self.__avatar_hash: str = _avatar_hash
            _avatar_animated = _avatar_hash.startswith('a_')

            self._avatar = Asset(
                self._connection,
                url=f'avatars/{self.id}/{_avatar_hash}',
                animated=_avatar_animated,
                hash=_avatar_animated
            )

        self._public_flags = data.get('public_flags', 0)
        self._system = data.get('system', False)
        self._bot = data.get('bot', False)

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

    @property
    def bot(self) -> bool:
        return self._bot

    @property
    def system(self) -> bool:
        return self._system

    def to_dict(self, /) -> PartialUserPayload:
        payload = {
            'id': self.id,
            'name': self.name,
            'discriminator': self.discriminator,
            'bot': self.bot,
            'system': self.system,
            'public_flags': self._public_flags
        }
        if self.__avatar_hash is not None:
            payload['avatar'] = self.__avatar_hash

    def _copy(self):
        self.__class__(self._connection, self.to_dict())

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


class ClientUser(PartialUser):
    __slots__ = PartialUser.__slots__

    def __init__(self, connection: Connection, /, data: UserPayload) -> None:
        super().__init__(connection, data)

    def _load_data(self, data: UserPayload) -> None:
        super()._load_data(data)
        self._mfa_enabled = data.get('mfa_enabled', False)
        self._verified = data.get('verified', False)
        self._locale = data.get('locale')
        self._flags = data.get('flags', 0)

    @property
    def mfa_enabled(self, /) -> bool:
        return self._mfa_enabled

    @property
    def verified(self, /) -> bool:
        return self._verified

    @property
    def locale(self, /) -> Optional[str]:
        return self._locale

    def to_dict(self, /) -> UserPayload:
        payload = {
            **super().to_dict(),
            'mfa_enabled': self.mfa_enabled,
            'verified': self.verified,
            'flags': self._flags
        }
        if self.locale is not None:
            payload['locale'] = self.locale

    async def edit(self, /, *, name: str = None, avatar: Union[str, bytes] = ...) -> None:
        payload = {}
        if name is not None:
            payload['username'] = name

        if avatar is not ...:
            if isinstance(avatar, str):
                with open(avatar, 'rb') as fp:
                    avatar = fp.read()

            if isinstance(avatar, bytes):
                avatar = _bytes_to_image_data(avatar)

            payload['avatar'] = avatar

        return await self._connection.api.users.me.patch(payload)
