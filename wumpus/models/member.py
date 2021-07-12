from datetime import datetime
from typing import Optional, List, Literal

from ..core.connection import Connection
from ..typings import JSON
from .objects import NativeObject
from .role import Role
from .user import User
from .guild import Guild


VALID_DELETE_MESSAGE_DAYS = Literal[0, 1, 2, 3, 4, 5, 6, 7]

class Member(NativeObject):
    def __init__(self, connection: Connection, guild: Guild, data: JSON, user: User = None, /) -> None:
        self._connection = connection
        self._load_data(guild, user, data)
    
    def _load_data(self, guild: Guild, user: User, data: JSON, /) -> None:
        _user = data.get('user')

        if _user is not None:
            self._user: Optional[User] = User(self._connection, user)
        else:
            self._user = user
        self._put_snowflake(self._user.id)
        self._guild = guild            
        self._nick: Optional[str] = data.get('nick')
        self._roles: List[Role] = [Role(self._connection, self._guild, role) for role in data.get('roles', [])] # type: ignore
        self._joined_at: datetime = datetime.fromisoformat(data.get('joined_at'))
        self._premium_since: Optional[datetime] = datetime.fromisoformat(data.get('premium_since'))
        self._deaf: bool = data.get('deaf')
        self._mute: bool = data.get('mute')
        self._pendings: Optional[bool] = data.get('pending')
        self._permissions: Optional[int] = data.get('permissions')
    
    async def kick(self, reason: str, /) -> None:
        return await self._guild.kick(self, reason=reason)
    
    async def ban(self, *, reason: str = None, delete_message_days: VALID_DELETE_MESSAGE_DAYS) -> None:
        return await self._guild.ban(self, reason=reason, delete_message_days=delete_message_days)