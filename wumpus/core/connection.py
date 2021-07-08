from asyncio import AbstractEventLoop
from typing import Optional

from .http import HTTPClient, Router


__all__ = (
    'Connection',
)


class Connection:
    def __init__(self, loop: AbstractEventLoop) -> None:
        self._loop: AbstractEventLoop = loop
        self._http: HTTPClient = None

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop

    @property
    def http(self) -> HTTPClient:
        return self._http

    @property
    def api(self) -> Router:
        return self._http.api
