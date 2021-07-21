from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Iterable, Union, TYPE_CHECKING

from .user import User
from .permissions import Permissions
from .objects import NativeObject, Object, Timestamp

from ..core.connection import Connection
from ..core.http import Router

from ..typings import JSON, ValidDeleteMessageDays
from ..typings.payloads import PartialUserPayload

if TYPE_CHECKING:
    from .guild import Guild
    from .role import Role


class Member(User):
    """
    Represents a guild member. This inherits from :class:`.User`.
    """

    __slots__ = (
        '_user',
        '_guild',
        '_nick',
        '_roles',
        '_joined_at',
        '_premium_since',
        '_deaf',
        '_mute',
        '_pending',
        '_permissions'
    ) + User.__slots__

    def __init__(self, /, connection: Connection, data: JSON, *, guild: Guild, user: PartialUserPayload = None) -> None:
        super().__init__(connection)
        self._connection: Connection = connection
        self._user: PartialUserPayload = user
        self._guild: Guild = guild
        self._load_data(data)
    
    def _load_data(self, data: JSON, /) -> None:
        _user = data.get('user')

        if _user is not None and not self._user:
            self._user = _user

        if self._user is not None:
            super()._load_data(self._user)

        self._nick: Optional[str] = data.get('nick')
        self._roles: List[int] = [int(role) for role in data.get('roles', [])]  # type: ignore
        self._joined_at: Timestamp = Timestamp.fromisoformat(data.get('joined_at'))
        self._premium_since: Optional[Timestamp] = Timestamp.fromisoformat(data.get('premium_since'))
        self._deaf: bool = data.get('deaf')
        self._mute: bool = data.get('mute')
        self._pending: Optional[bool] = data.get('pending')

        _permissions = data.get('permissions')
        if _permissions is not None:
            self._permissions: Optional[Permissions] = Permissions(_permissions)

    @property
    def _api(self, /) -> Router:
        return self._connection.api.guilds(self._guild.id).members(self.id)

    @property
    def guild(self, /) -> Guild:
        """:class:`.Guild`: The guild this member is in."""
        return self._guild

    @property
    def nick(self, /) -> str:
        """str: The member's nickname. `None` if the member does not have one.

        See Also
        --------
        :attr:`.Member.display_name`
        """
        return self._nick

    @property
    def display_name(self, /) -> str:
        """str: The name that appears for messages from this member."""
        return self.nick or self.name

    @property
    def joined_at(self, /) -> Timestamp:
        """:class:`.Timestamp`: The timestamp for when this member joined it's guild."""
        return self._joined_at

    @property
    def premium_since(self, /) -> Optional[Timestamp]:
        """:class:`.Timestamp`: The timestamp for when this member started boosting this guild.

        This will be `None` is the member is not boosting at all.
        """
        return self._premium_since

    @property
    def deaf(self, /) -> bool:
        """bool: Whether or not this member is deafened."""
        return self._deaf

    @property
    def mute(self, /) -> bool:
        """bool: Whether or not this member is muted."""
        return self._mute

    @property
    def permissions(self, /) -> Permissions:
        """:class:`.Permissions`: The permissions for this member at the guild level.

        .. note::
            This does not account for channel overwrites.
            See :meth:`.Member.permissions_in` for that.
        """
        return self._permissions

    async def kick(self, reason: str, /) -> None:
        """|coro|

        Removes this member from it's guild.
        This requires the `kick_members` permission.

        This is equivalent to :meth:`.Guild.kick`.

        Paramters
        ---------
        reason: str
            The audit log reason to use.
        """
        return await self._guild.kick(self, reason=reason)
    
    async def ban(self, *, reason: str = None, delete_message_days: ValidDeleteMessageDays = 1) -> None:
        """|coro|

        Bans this member from it's guild.
        This requires the `ban_members` permission.

        This is equivalent to :meth:`.Guild.ban`.

        Paramters
        ---------
        delete_message_days: int
            The amount of days worth of message history from this user to delete.
        reason: str
            The audit log reason to use.
        """
        return await self._guild.ban(self, reason=reason, delete_message_days=delete_message_days)

    async def unban(self, *, reason: str = None) -> None:
        """|coro|

        Unbans this member from it's stored guild.
        This can be useful is the member is still stored after being banned.

        This is equivalent to :meth:`.Guild.unban`.

        Parameters
        ----------
        reason: str
            The audit log reason to use.
        """
        return await self._guild.unban(self, reason=reason)

    async def add_role(self, role: Union[Role, Object], /, *, reason: str = None) -> None:
        """|coro|

        Adds a role to this member.

        Parameters
        ----------
        role: :class:`Role`
            The role to add.
        reason: str
            The audit log reason to use.
        """
        return await self._api.roles(role.id).put(reason=reason)

    async def remove_role(self, role: Union[Role, Object], /, *, reason: str = None) -> None:
        """|coro|

        Removes a role from this member.

        Parameters
        ----------
        role: :class:`Role`
           The role to remove.
        reason: str
           The audit log reason to use.
        """
        return await self._api.roles(role.id).delete(reason=reason)

    async def add_roles(self, /, *roles: Union[Role, Object], reason: str = None) -> None:
        """|coro|

        Adds multiple roles to this member at once.

        Parameters
        ----------
        *roles: :class:`Role`
           The roles to add.
        reason: str
           The audit log reason to use.
        """

        try:
            sanitized = list(set(self._roles) | set(role.id for role in roles))
            return await self._api.patch({'roles': sanitized}, reason=reason)
        finally:
            del sanitized

    async def remove_roles(self, /, *roles: Union[Role, Object], reason: str = None) -> None:
        """|coro|

        Removes multiple roles from this member at once.

        Parameters
        ----------
        *roles: :class:`Role`
           The roles to remove.
        reason: str
           The audit log reason to use.
        """

        try:
            sanitized = list(set(self._roles) - set(role.id for role in roles))
            return await self._api.patch({'roles': sanitized}, reason=reason)
        finally:
            del sanitized

    async def edit(
        self,
        /,
        *,
        nick: str = None,
        roles: Iterable[Union[Role, Object]] = None,
        mute: bool = None,
        deaf: bool = None,
        # channel: ... = None  # TODO: VoiceChannel
        reason: str = None
    ) -> None:
        """|coro|

        Edits attributes of this member.
        All parameters are keyword-only and optional.

        Parameters
        ----------
        nick: str
            The new nickname of this member.
        roles: Iterable[:class:`Role`]
            An iterable of roles to overwrite the member's roles with.
        mute: bool
            Whether or not to mute this member.
        deaf: bool
            Whether or not to deafen this member.
        reason: str
            The audit log reason to use.
        """

        payload = {}

        if nick is not None:
            payload['nick'] = str(nick)

        if roles is not None:
            payload['roles'] = [str(r.id) for r in roles]

        if mute is not None:
            payload['mute'] = bool(mute)

        if deaf is not None:
            payload['deaf'] = bool(deaf)

        return await self._api.patch(payload, reason=reason)
