from datetime import datetime
from typing import Optional, List

from .role import Role
from .user import User
from .guild import Guild
from .permissions import Permissions
from .objects import NativeObject, Timestamp

from ..core.connection import Connection
from ..typings import JSON, ValidDeleteMessageDays


class Member(NativeObject):
    def __init__(self, connection: Connection, guild: Guild, data: JSON, user: User = None, /) -> None:
        self._connection: Connection = connection
        self._guild: Guild = guild
        self._user: User = user
        self._load_data(data)
    
    def _load_data(self, data: JSON, /) -> None:
        _user = data.get('user')

        if _user is not None:
            self._user: Optional[User] = User(self._connection, _user)
        if self._user is not None:
            self._put_snowflake(self._user.id)

        self._nick: Optional[str] = data.get('nick')
        self._roles: List[Role] = [Role(self._connection, self._guild, role) for role in data.get('roles', [])]  # type: ignore
        self._joined_at: Timestamp = Timestamp.fromisoformat(data.get('joined_at'))
        self._premium_since: Optional[Timestamp] = Timestamp.fromisoformat(data.get('premium_since'))
        self._deaf: bool = data.get('deaf')
        self._mute: bool = data.get('mute')
        self._pendings: Optional[bool] = data.get('pending')

        _permissions = data.get('permissions')
        if _permissions is not None:
            self._permissions: Optional[Permissions] = Permissions(_permissions)
    
    async def kick(self, reason: str, /) -> None:
        return await self._guild.kick(self, reason=reason)
    
    async def ban(self, *, reason: str = None, delete_message_days: ValidDeleteMessageDays) -> None:
        return await self._guild.ban(self, reason=reason, delete_message_days=delete_message_days)
