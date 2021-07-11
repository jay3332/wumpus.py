from .objects import NativeObject
from ..typings import JSON, Snowflake
from typing import Optional, Any, TypeVar
from .color import Color
from ..core.connection import Connection
from .guild import Guild


T = TypeVar('t', bound='role')


class RoleTags:
    def __init__(self, data: JSON, /) -> None:
        self._load_data(data)
    
    def _load_data(self, data: JSON) -> None:
        self.bot_id: Optional[Snowflake] = int(data.get('bot_id'))
        self.integration_id: Optional[Snowflake] = int(data.get('integration_id'))
        # The api said this field is null, I suppose it could be anything or None.
        self.premium_subscriber: Optional[Any] = data.get('premium_subscriber', None)

class Role(NativeObject):
    def __init__(self: T, connection: Connection, guild: Guild, data: JSON, /) -> None:
        self._connection = connection
        self._load_data(guild, data)
    
    def _load_data(self: T, guild: Guild, data: JSON) -> None:
        self._put_snowflake(data.get('id'))
        self.guild = guild
        self.name: str = data.get('name')
        self.color: Color = Color(data.get('color'))
        self.hoist: bool = data.get('hoist')
        self.position: int = data.get('position')
        self.permissions: int = data.get('permissions')
        self.managed: bool = data.get('managed')
        self.mentionable: bool = data.get('mentionable')
        self.tags: RoleTags = RoleTags(data.get('tags'))
    
    async def edit_position(self: T, position: int) -> None:
        await self._connection.api.guilds(self.guild.id).roles.patch({'id': self.id, 'position': position})
    
    async def edit(self: T, name: Optional[None] = None, 
                        permissions: Optional[str] = None, 
                        color: Optional[Color] = None, 
                        hoist: Optional[bool] = None, 
                        mentionable: Optional[bool] = None) -> T:
        payload = {
            'name': name,
            'permissions': permissions,
            'color': color.value,
            'hoist': hoist,
            'mentionable': mentionable
        }
        _role = await self._connection.api.guilds(self.guild.id).roles(self.id).patch(payload)
        self._load_data(self.guild, _role)

        return self
    
    async def delete(self: T) -> None:
        await self._connection.api.guilds(self.guild.id).roles(self.id).delete()

    