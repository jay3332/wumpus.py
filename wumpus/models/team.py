from typing import List, Optional

from ..core.enums import MemberShipState
from ..typings import Snowflake
from .asset import Asset
from ..core.connection import Connection
from .objects import NativeObject
from .user import PartialUser


class TeamMember:
    def __init__(self, connection: Connection, data, /) -> None:
        self._load_data(data)
        self._connection = connection
    
    def _load_data(self, data, /) -> None:
        self.member_ship_state: MemberShipState = MemberShipState(data.get('member_ship_state'))
        self.permissions: List[str] = data.get('permissions')
        self.team_id: Snowflake = data.get('team_id')
        self.user: PartialUser = PartialUser(self._connection, data.get('user'))


class Team(NativeObject):
    def __init__(self, connection: Connection, data, /) -> None:
        self._load_data(data)
        self._connection = connection
    
    def _load_data(self, data, /) -> None:
        icon = data.get('icon')
        self._put_snowflake(data.get('id'))
        self.icon = Asset(self._connection, url=f"team-icons/{self.id}/{icon}.png", hash=icon)
        self.members: List[TeamMember] = [member for member in data.get('members')]
        self.name: str = data.get('name')
        self.owner_user_id: Snowflake = data.get('owner_user_id')
