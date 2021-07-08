from asyncio import get_event_loop, AbstractEventLoop
from ..typings.core import HTTPVersion, GatewayVersion


__all__ = (
    'Client',
)


class Client:
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
        self._loop: AbstractEventLoop = loop or get_event_loop() 
        

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop
