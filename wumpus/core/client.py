from asyncio import get_event_loop, AbstractEventLoop
from typing import Dict, List, NamedTuple, Union, overload

from ..typings.core import HTTPVersion, GatewayVersion, EmitterCallback


__all__ = (
    'Client',
    'Emitter'
)


class WeakListener(typing.NamedTuple):
    event: str
    callback: EmitterCallback
    count: int = None 


class Emitter:
    def __init__(self):
        self.__direct_listeners: Dict[str, EmitterCallback]
        self.__listeners: List[WeakListener] = []

    def _add_direct_listener(self, event: str, callback: EmitterCallback) -> None:
        self.__direct_listeners[event] = callback

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
        

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop
