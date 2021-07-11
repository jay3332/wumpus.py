from typing import List

from ..core.enums import MemberShipState
from ..core.connection import Connection

from .asset import Asset
from .objects import NativeObject
from .user import PartialUser

from ..typings import Snowflake


class TeamMember:
    def __init__(self, connection: Connection, data, /) -> None:
        self._load_data(data)
        self._connection = connection
    
    def _load_data(self, data, /) -> None:
        self.member_ship_state: MemberShipState = MemberShipState(data.get('member_ship_state'))
        self.permissions: List[str] = data.get('permissions')
        self._team_id: Snowflake = data.get('team_id')
        self.user: PartialUser = PartialUser(self._connection, data.get('user'))


class Team(NativeObject):
    def __init__(self, connection: Connection, data, /) -> None:
        self._load_data(data)
        self._connection = connection
        super().__init__()

    def _load_data(self, data, /) -> None:
        self._put_snowflake(data.get('id'))

        icon = data.get('icon')  # This will never be animated.
        self.icon = Asset(self._connection, url=f"team-icons/{self.id}/{icon}.png", hash=icon)
        self.name: str = data.get('name')

        self.owner_user_id: Snowflake = data.get('owner_user_id')
        self.members: List[TeamMember] = [TeamMember(self._connection, member) for member in data.get('members', [])]

    def _copy(self, /):
        ...
