from typing import TypeVar

from .asset import Asset
from .objects import NativeObject

from ..core.connection import Connection
from ..typings.payloads import GuildPayload


T = TypeVar('T', bound='Guild')

__all__ = (
    'Guild',
)


class Guild(NativeObject):
    __slots__ = (
        '_name',
    ) + NativeObject.__slots__

    def __init__(self, connection: Connection, /, data: GuildPayload) -> None:
        self._connection: Connection = connection
        self._last_received_data: GuildPayload = {}
        self._load_data(data)
        super().__init__()

    def _load_asset(self, key: str, /, *, data: GuildPayload, entity: str) -> Asset:
        _hash = data.get(key)

        if _hash is not None:
            animated = _hash.startswith('a_')
            return Asset(
                self._connection,
                url=f'{entity}/{self.id}/{_hash}',
                animated=animated,
                hash=_hash
            )
        else:
            return None

    def _load_data(self, data: GuildPayload) -> None:
        self._last_received_data |= data
        self._put_snowflake(data['id'])

        self._name: str = data['name']

        # TODO: MemberManager, RoleManager, EmojiManager, etc 

        self.icon: Asset = self._load_asset('icon', data=data, entity='icons')
        self.banner: Asset = self._load_asset('banner', data=data, entity='banners')
        self.splash: Asset = self._load_asset('splash', data=data, entity='splashes')
        self.discovery_splash: Asset = self._load_asset('discovery_splash', data=data, entity='discovery-splashes')

    @property
    def name(self, /) -> str:
        return self._name

    def _copy(self: T) -> T:
        return self.__class__(self._connection, self._last_received_data)

    def __str__(self, /) -> str:
        return self.name

    def __repr__(self, /) -> str:
        return f'<Guild name={self.name!r} id={self.id}>'
