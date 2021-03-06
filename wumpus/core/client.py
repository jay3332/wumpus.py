from __future__ import annotations

from collections import defaultdict
from asyncio import get_event_loop, AbstractEventLoop
from typing import Callable, Dict, List, NamedTuple, Optional, Union, overload

from .http import Router
from .connection import Connection

from ..models.user import ClientUser
from ..models.guild import GuildPreview
from ..models.intents import Intents

from ..typings.core import Snowflake, HTTPVersion, GatewayVersion, EmitterCallback


__all__ = (
    'Client',
    'Emitter'
)


class WeakListener(NamedTuple):
    callback: EmitterCallback
    count: int = None 


class Emitter:
    def __init__(self):
        self.__direct_listeners: Dict[str, EmitterCallback] = {}
        self.__listeners: Dict[str, List[WeakListener]] = defaultdict(list)

    def _add_direct_listener(self, event: str, callback: EmitterCallback, /) -> None:
        self.__direct_listeners[event] = callback

    def _add_weak_listener(self, event: str, callback: EmitterCallback, /, *, count: int = None) -> None:
        self.__listeners[event].append(WeakListener(callback, count=count))

    @overload
    def event(self, event: str) -> Callable[[EmitterCallback], EmitterCallback]:
        ...

    @overload
    def event(self, callback: EmitterCallback) -> EmitterCallback:
        ...

    def event(self, event: Union[str, EmitterCallback]):  # We will overload this
        if isinstance(event, str):
            def decorator(callback: EmitterCallback):
                self._add_direct_listener(event, callback)
                return callback

            return decorator
        
        name = event.__name__
        if not name.startswith('on_'):
            raise ValueError('event callback functions must start with "on_"')

        self._add_direct_listener(name[3:], event)


class Client(Emitter):
    """
    Represents a client connection to Discord.
    """

    def __init__(
        self,
        *,
        intents: Intents = None,
        # allowed_mentions: AllowedMentions = None,
        http_version: HTTPVersion = 9,
        gateway_version: GatewayVersion = 9,
        loop: AbstractEventLoop = None
    ) -> None:
        super().__init__()
        self._loop: AbstractEventLoop = loop or get_event_loop()
        self._intents: Intents = intents or Intents.default()
        self._connection: Connection = None

        self._http_version: int = http_version
        self._gateway_version: int = gateway_version

    @property
    def loop(self) -> AbstractEventLoop:
        """asyncio.AbstractEventLoop: The event loop this client is using."""
        return self._loop

    @property
    def api(self) -> Optional[Router]:
        """:class:`~.Router`: The HTTP API router this client uses."""
        return self._connection.api if self._connection else None

    @property
    def user(self) -> ClientUser:  # type: ignore
        """:class:`~.ClientUser` The Discord user this client represents."""
        return self._connection.user

    def _establish_connection(self, *, force: bool = False) -> None:
        if self._connection is not None and not force:
            return
        self._connection = Connection(self._loop)

    async def login(self, token: str = None, /) -> None:
        """|coro|

        Establishes an HTTP session to Discord.
        """

        self._establish_connection()
        self._connection.establish_http(token, v=self._http_version)
        await self._connection.update_user()

    async def fetch_guild_preview(self, /, id: Snowflake) -> GuildPreview:
        """|coro|

        Fetches a :class:`~.GuildPreview` by it's ID.

        .. note::
             If the client is not in the guild, then the guild must be lurkable.

        Parameters
        ----------
        id: Snowflake
            The snowflake ID of the guild to fetch.

        Returns
        -------
        :class:`~.GuildPreview`
        """

        data = await self.api.guilds(id).preview.get()
        return GuildPreview(self._connection, data=data)
