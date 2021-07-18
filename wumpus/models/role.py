from typing import Optional, Any, TypeVar, Union

from .color import Color
from .guild import Guild
from .objects import NativeObject
from .permissions import Permissions

from ..core.connection import Connection
from ..typings import JSON, Snowflake


T = TypeVar('T', bound='Role')


class RoleTags:
    def __init__(self, data: JSON, /) -> None:
        self._load_data(data)
    
    def _load_data(self, data: JSON, /) -> None:
        if data is None:
            self.bot_id = None
            self.integration_id = None
            self.premium_subscriber = None
            return

        _bot_id = data.get('bot_id')

        if _bot_id is not None:
            self.bot_id: Optional[Snowflake] = int(_bot_id)

        _integration_id = data.get('integration_id')

        if _integration_id is not None:
            self.integration_id: Optional[Snowflake] = int(_integration_id)
        
        # docs said this field is null, I suppose it could be anything or None.
        self.premium_subscriber: Optional[Any] = data.get('premium_subscriber')


class Role(NativeObject):
    """Represents a Discord role inside of a guild.

    Attributes
    ----------
    id: int
        The Snowflake ID of this role.
    name: str
        The name of this role.
    guild: :class:`Guild`
        The guild this role belongs to.
    position: int
        The position of this role.
    permissions: :class:`Permissions`
        The permissions this role has.
    managed: bool
        Whether the role is managed by the guild.
    mentionable: bool
        Whether this role is mentionable.
    color: :class:`Color`
        The color of this role.
    hoist: bool
        Whether this role is hoisted.
    """
    
    def __init__(self: T, connection: Connection, guild: Guild, data: JSON, /) -> None:
        super().__init__()
        self._guild: Guild = guild
        self._connection = connection
        self._load_data(data)
    
    def _load_data(self: T, data: JSON) -> None:
        self._put_snowflake(data.get('id'))
        
        self._name: str = data.get('name')
        self._color: Color = Color(data['color'])
        self._hoist: bool = data['hoist']
        self._position: int = data['position']
        self._managed: bool = data['managed']
        self._mentionable: bool = data['mentionable']

        self._tags: RoleTags = RoleTags(data.get('tags'))
        self._permissions: Permissions = Permissions(data.get('permissions', 0))

    @property
    def guild(self, /) -> Guild: 
        return self._guild

    @property
    def name(self, /) -> str:
        return self._name

    @property
    def color(self, /) -> Color:
        return self._color

    colour = color

    @property
    def tags(self, /) -> RoleTags:
        return self._tags

    @property
    def hoist(self, /) -> bool:
        return self._hoist

    @property
    def managed(self, /) -> bool:
        return self._managed

    @property
    def mentionable(self, /) -> bool:
        return self._mentionable

    async def _patch(self: T, payload: JSON, /, *, reason: str = None) -> T:
        response = await self._connection.api.guilds(self.guild.id).roles(self.id).patch(payload, reason=reason)
        self._load_data(response)
        return self

    async def move(self: T, /, position: int, *, reason: str = None) -> T:
        return await self._patch({'position': position}, reason=reason)
    
    async def rename(self: T, name: str, /, *, reason: str = None) -> T:
        return await self._patch({'name': name}, reason=reason)

    async def edit(
        self: T, 
        *,
        name: Optional[None] = None, 
        permissions: Optional[str] = None, 
        color: Optional[Union[Color, int]] = None, 
        hoist: Optional[bool] = None, 
        mentionable: Optional[bool] = None,
        reason: Optional[str] = None
    ) -> T:
        payload = {}

        if name is not None:
            payload['name'] = name

        if permissions is not None:
            payload['permissions'] = permissions

        if color is not None:
            payload['color'] = color.value if isinstance(color, Color) else color

        if hoist is not None:
            payload['hoist'] = hoist

        if mentionable is not None:
            payload['mentionable'] = mentionable

        return await self._patch(payload, reason=reason)
    
    async def delete(self: T, /, *, reason: str = None) -> None:
        await self._connection.api.guilds(self.guild.id).roles(self.id).delete(reason=reason)
