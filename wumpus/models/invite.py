from typing import List, Optional

from ..core.connection import Connection
from ..core.enums import InviteTargetTypes, VerificationLevel
from ..typings import JSON, Snowflake
from ..utils import _try_int
from .application import Application
from .member import Member
from .objects import NativeObject, Timestamp
from .user import User


class PartialInviteGuild(NativeObject):
    def __init__(self, connection: Connection, data: JSON, /) -> None:
        self._connection = connection
        self._load_data(data)

    def _load_data(self, data: JSON, /) -> None:
        self._put_snowflake(data.get("id"))

        self._name: str = data.get("name")
        self._description: Optional[str] = data.get("description")
        self._features: Optional[List[str]] = data.get("features")

        self._verification_level: Optional[VerificationLevel] = VerificationLevel(data.get("verification_level", 0))


class PartialInviteChannel(NativeObject):
    def __init__(self, connection: Connection, data: JSON, /) -> None:
        self._connection = connection
        self._load_data(data)

    def _load_data(self, data: JSON, /) -> None:
        self._put_snowflake(data.get("id"))
        self._name: str = data.get("name")
        # TODO: type


class InviteStageInstance(NativeObject):
    def __init__(self, connection: Connection, data: JSON, /) -> None:
        self._connection = connection
        self._load_data(data)

    def _load_data(self, data: JSON, /) -> None:
        # TODO: Members
        self._particpant_count: int = data.get("particpant_count")
        self._speaker_count: int = data.get("speaker_count")
        self._topic: str = data.get("topic")


class Invite:
    def __init__(self, connection: Connection, data: JSON, /) -> None:
        self._connection = connection
        self._load_data(data)

    def _load_data(self, data: JSON, /) -> None:
        self._code: str = data.get("code")
        guild = data.get("guild")
        if guild:
            self._guild: Optional[PartialInviteGuild] = PartialInviteGuild(self._connection, guild)
        else:
            self._guild = None

        self._channel: PartialInviteChannel = PartialInviteChannel(self._connection, data.get("channel"))
        inviter = data.get("inviter")
        if inviter:
            self._inviter: Optional[User] = User(self._connection, inviter)
        else:
            self._inviter = None

        self._target_type = InviteTargetTypes(int(data.get("target_type", 0)))
        target_user = data.get("target_user")
        if target_user:
            self._target_user: User = User(self._connection, target_user)
        else:
            self._target_user = None

        self._stage_instance: InviteStageInstance = InviteStageInstance(self._connection, data.get("stage_instance"))
        self._target_application: Optional[Application] = Application(
            self._connection, data.get("target_application", {})
        )
        self._approximate_presence_count: Optional[int] = data.get("approximate_presence_count")
        self._approximate_member_count: Optional[int] = data.get("approximate_member_count")
        self._expires_at: Optional[Timestamp] = Timestamp.utcfromtimestamp(data.get("expires_at"))
        self._uses: Optional[int] = data.get("uses")
        self._max_uses: Optional[int] = data.get("max_uses")
        self._max_age: Optional[int] = data.get("max_age")
        self._temporary: Optional[bool] = data.get("temporary")
        self._created_at: Optional[Timestamp] = Timestamp.utcfromtimestamp(data.get("created_at"))
