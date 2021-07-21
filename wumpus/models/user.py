from .asset import Asset
from .objects import NativeObject
from .messageable import Messageable

from ..core.connection import Connection

from ..utils import _bytes_to_image_data
from ..typings.payloads import PartialUserPayload, UserPayload

from typing import Literal, Optional, Union

__all__ = (
    'PartialUser',
    'ClientUser'
)

UserFormat = Literal['m', 'n', 't']


class PartialUser(NativeObject):
    __slots__ = (
        '_name',
        '_discriminator',
        '_avatar',
        '_public_flags',
        '_system',
        '_bot',
        '__avatar_hash'
    ) + NativeObject.__slots__

    _avatar: Asset

    def __init__(self, connection: Connection, /, data: PartialUserPayload = None) -> None:
        self._connection: Connection = connection
        if data is not None:
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
            self.__avatar_hash = None
            self._avatar = Asset(self._connection, url=f'embed/avatars/{self._discriminator % 5}')
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
        """str: The user's username."""
        return self._name

    @property
    def discriminator(self) -> str:
        """str: The user's discriminator."""
        return self._discriminator

    @property
    def avatar(self) -> Asset:
        """:class:`.Asset`: The user's display avatar."""
        return self._avatar

    @property
    def tag(self) -> str:
        """str: The user's name and discriminator in the conventional name#discrim format."""
        return f'{self.name}#{self.discriminator}'

    @property
    def mention(self) -> str:
        """str: The mention format of the user."""
        return f'<@{self.id}>'

    @property
    def bot(self) -> bool:
        """bool: Whether or not this user is a bot."""
        return self._bot

    @property
    def system(self) -> bool:
        """bool: Whether or not this user is an official system account."""
        return self._system

    def to_dict(self, /) -> PartialUserPayload:
        """Converts this user into a raw dictionary that can be sent to Discord.

        Returns
        -------
        JSON
        """
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

    def __format__(self, format: UserFormat, /) -> str:
        format = format.lower()

        if not format or format == 't':
            return str(self)

        if format == 'm':
            return self.mention
        elif format == 'n':
            return self.name

        raise ValueError(f'invalid format for User {format!r}')


class ClientUser(PartialUser):
    """
    Represents the user that represents the client.
    """

    __slots__ = (
        '_mfa_enabled',
        '_verified',
        '_locale',
        '_flags'
    ) + PartialUser.__slots__

    def _load_data(self, data: UserPayload) -> None:
        super()._load_data(data)
        self._mfa_enabled = data.get('mfa_enabled', False)
        self._verified = data.get('verified', False)
        self._locale = data.get('locale')
        self._flags = data.get('flags', 0)

    @property
    def mfa_enabled(self, /) -> bool:
        """bool: Whether or not 2 factor authentication is enabled on this account."""
        return self._mfa_enabled

    @property
    def verified(self, /) -> bool:
        """bool: Whether or not this account has a verified email."""
        return self._verified

    @property
    def locale(self, /) -> Optional[str]:
        """str: The locale (language choice) of this user."""
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
        """|coro|

        Changes the name and/or avatar of this user.
        All parameters are keyword only, and they are all optional.

        Parameters
        ----------
        name: str
            The username to change to.
        avatar: Union[bytes, str]
            The avatar to change to. This can be a raw byte string, or
            a file path that leads to the image.
        """

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

    async def update(self, /) -> None:
        await self._connection.update_user()


class User(PartialUser, Messageable):
    """
    Represents a Discord user.
    """

    __slots__ = ('_dm_channel_id',) + PartialUser.__slots__

    def _load_data(self, data: PartialUserPayload) -> None:
        self._dm_channel_id: int = None
        super()._load_data(data)

    async def create_dm(self, /) -> ...:
        """|coro|

        Opens a DM with this user. This is implicitly called,
        this should not be used frequently.
        """

        payload = {
            'recipient_id': self.id
        }

        route = self._connection.api.users.me.channels
        data = await route.post(payload)
        self._dm_channel_id = data['id']

    @property
    def _messageable_id(self, /) -> int:
        return self._dm_channel_id
