from asyncio import AbstractEventLoop


__all__ = (
    'Connection',
)


class Connection:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self._loop: AbstractEventLoop = loop

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop
