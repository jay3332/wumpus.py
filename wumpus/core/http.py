from __future__ import annotations

from aiohttp import ClientSession
from typing import Any, Awaitable, Dict, Optional, TypeVar

from ..typings.core import HTTPRequestMethod, JSON

RT = TypeVar('RT', bound='Router')


__all__ = (
    'Router',
    'HTTPClient'
)


class Router:
    def __init__(
        self, 
        route: str = '', 
        /,
        *,
        base: str, 
        http: HTTPClient
    ) -> None:
        self.__route: str = route.rstrip('/')
        self.__base: str = base.rstrip('/')
        self.__http: HTTPClient = http

    @property
    def route(self, /) -> str:
        return self.__route

    @property
    def url(self, /) -> str:
        return self.__base + self.__route

    def _construct(self: RT, new_route: str, /) -> RT:
        return self.__class__(new_route, base_url=self.__base, http=self.__http)
   
    def __getattr__(self: RT, route: str, /) -> RT:
        if route in dir(self):
            return super().__getattr__(route)

        new_route = self.__route + '/' + route
        return self._construct(new_route)

    def __call__(self: RT, id: int, /) -> RT:
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
        return self.__http.request(method, self.url, params=params, data=data)

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

    def put(
        self, 
        data: JSON = None,
        /
    ) -> Awaitable[Optional[JSON]]:
        return self.request('PUT', data=data)

    def patch(
        self, 
        data: JSON = None,
        /
    ) -> Awaitable[Optional[JSON]]:
        return self.request('PATCH', data=data)
    
    def delete(
        self, 
        data: JSON = None,
        /
    ) -> Awaitable[Optional[JSON]]:
        return self.request('DELETE', data=data)



class HTTPClient:
    __slots__ = ('__session', '__api_router')

    def __init__(self, /, *, v: int = 9):
        self.__session: ClientSession = ClientSession()
        self.__api_router: Router = Router(base=f'https://discord.com/api/v{v}', http=self)

    @property
    def api(self) -> Router:
        return self.__api_router

    async def request(
        self,
        method: HTTPRequestMethod,
        route: str,
        /,
        *,
        params: Dict[str, Any],
        data: JSON
    ) -> Optional[JSON]:
        ...

    async def close(self) -> None:
        await self.__session.close()
