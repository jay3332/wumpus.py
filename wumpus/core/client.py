from asyncio import AbstractEventLoop, get_event_loop
from collections import defaultdict
from typing import Callable, Dict, List, NamedTuple, Optional, Union, overload

from ..typings.core import EmitterCallback, GatewayVersion, HTTPVersion
from .connection import Connection
from .http import Router
from .user import ClientUser

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
        allowed_mentions: AllowedMentions = None,
        http_version: HTTPVersion = 9,
        gateway_version: GatewayVersion = 9,
        loop: AbstractEventLoop = None
    ) -> None:
        super().__init__()

        self._loop: AbstractEventLoop = loop or get_event_loop() 
        self._connection: Connection = None

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop

    @property
    def api(self) -> Optional[Router]:
        return self._connection.api if self._connection else None
    
    @property
    def user(self) -> ClientUser:
        return self._connection._user
