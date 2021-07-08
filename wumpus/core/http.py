from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Dict, Optional, TypeVar
import datetime

from aiohttp import ClientSession

from ..typings.core import JSON, HTTPRequestMethod
from .connection import Connection

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
    MAX_RETRIES = 3
    __slots__ = ('__session', '__api_router', '_global_ratelimited', '_buckets_lock')

    def __init__(self, v: int = 9, connection: Connection, /):
        self.__session: ClientSession = ClientSession()
        self._connection = connection
        self.__api_router: Router = Router(base=f'https://discord.com/api/v{v}', http=self)
        self._global_ratelimited = asyncio.Event()
        self._buckets_lock = {}

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
        data: JSON,
        headers: Dict[str, str]
    ) -> Optional[JSON]:
        bucket_key = f"{method} {route}"
        bucket = self._buckets_lock.get(bucket_key)
        if bucket is None:
            self._buckets_lock[bucket_key] = bucket = asyncio.Lock()
        _headers = {'Authorization': self._connection.token}
        _headers['Content-Type'] = 'application/json'
        _headers.update(headers)
        await bucket.acquire()
        if not self._global_ratelimited.is_set():
            await self._global_ratelimited.wait()
        for tries in range(self.MAX_RETRIES):
            async with self.__session.request(method, route, params=params, js=data, headers=_headers) as resp:
                bucket_remianing = resp.headers.get("X-RateLimit-Remaining")
                data = await resp.json()
                if int(bucket_remianing) == 0:
                    await asyncio.sleep(float(resp.headers.get("X-RateLimit-Reset-After")))
            if 300 > response.status >= 200:
                return data
            if resp.status == 429:
                is_global = data.get("global", False)
                if is_global is True:
                    self._global_ratelimited.clear()
                await asyncio.sleep(float(data.get("retry_after")))
                if is_global:
                    self._global_ratelimited.set()
                continue
            
            # TODO: Handle all 40x status code and 50x status code
        


    async def close(self) -> None:
        await self.__session.close()
