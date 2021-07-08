from __future__ import annotations

from aiohttp import ClientSession
from typing import Any, Awaitable, Dict, Optional, TypeVar

from ..typings.core import HTTPRequestMethod, JSON

ART = TypeVar('ART', bound='APIRouter')


__all__ = (
    'APIRouter',
    'HTTPClient'
)


class APIRouter:
    def __init__(
        self, 
        route: str = '', 
        /,
        *,
        base_url: str, 
        http: HTTPClient
    ) -> None:
        self.__route: str = route.rstrip('/')
        self.__base: str = base_url.rstrip('/')
        self.__http: HTTPClient = http

    @property
    def route(self, /) -> str:
        return self.__route

    def _construct(self: ART, new_route: str, /) -> ART:
        return self.__class__(new_route, base_url=self.__base, http=self.__http)
   
    def __getattr__(self: ART, route: str, /) -> ART:
        if route in dir(self):
            return super().__getattr__(route)

        new_route = self.__route + '/' + route
        return self._construct(new_route)

    def __call__(self: ART, id: int, /) -> ART:
        new_route = self.__route + '/' + str(id)
        return self._construct(new_route)
        
    def request(
        self, 
        method: HTTPRequestMethod,
        /,
        *,
        params: Dict[str, Any] = None,
        data: JSON = None
    ) -> Awaitable[Optional[JSON]]:
        return self.__http.request(method, self.__base + self.route, params=params, data=data)

    def get(
        self,
        params: Dict[str, Any] = None,
        /
    ) -> Awaitable[Optional[JSON]]:
        return self.request('GET', params=params)

    def post(
        self, 
        data: JSON = None,
        /,
        *,
        params: Dict[str, Any] = None
    ) -> Awaitable[Optional[JSON]]:
        return self.request('POST', data=data, params=params)


class HTTPClient:
    def __init__(self, /):
        self.__session: ClientSession = ClientSession()
        self.__api_router: APIRouter = APIRouter()

    async def request(
        self,
        method: HTTPRequestMethod,
        route: str,
        /,
        *,
        params: Dict[str, Any],
        data: JSON
    ) -> Awaitable[Optional[JSON]]:
        ...
