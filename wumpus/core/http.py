from __future__ import annotations

import asyncio

from aiohttp import ClientSession
from typing import Any, Awaitable, Dict, Optional, TypeVar

from ..typings.core import JSON, HTTPRequestMethod
from ..errors import *


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
        if route == 'me':
            route = '@me'

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
        data: JSON = None,
        headers: Dict[str, str] = None
    ) -> Awaitable[Optional[JSON]]:
        return self.__http.request(method, self.url, params=params, data=data, headers=headers)

    def get(
        self,
        params: Dict[str, Any] = None,
        /,
        *,
        headers: Dict[str, str] = None
    ) -> Awaitable[Optional[JSON]]:
        return self.request('GET', params=params, headers=headers)

    def post(
        self, 
        data: JSON = None,
        /,
        *,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Awaitable[Optional[JSON]]:
        return self.request('POST', data=data, params=params, headers=headers)

    def put(
        self, 
        data: JSON = None,
        /,
        *,
        headers: Dict[str, str] = None
    ) -> Awaitable[Optional[JSON]]:
        return self.request('PUT', data=data, headers=headers)

    def patch(
        self, 
        data: JSON = None,
        /,
        *,
        headers: Dict[str, str] = None
    ) -> Awaitable[Optional[JSON]]:
        return self.request('PATCH', data=data, headers=headers)
    
    def delete(
        self, 
        data: JSON = None,
        /,
        *,
        headers: Dict[str, str] = None
    ) -> Awaitable[Optional[JSON]]:
        return self.request('DELETE', data=data, headers=headers)


class HTTPClient:
    __slots__ = ('__token', '__session', '__api_router', '_global_ratelimited', '_buckets_lock')

    MAX_RETRIES: int = 3

    def __init__(self, /, *, v: int = 9, token: str):
        self.__session: ClientSession = ClientSession()
        self.__api_router: Router = Router(base=f'https://discord.com/api/v{v}', http=self)
        self.__token: str = token

        self._global_ratelimited = asyncio.Event()
        self._buckets_lock = {}

    @property
    def api(self) -> Router:
        return self.__api_router

    async def request(
        self,
        method: HTTPRequestMethod,
        url: str,
        /,
        *,
        params: Dict[str, Any] = None,
        data: JSON = None,
        headers: Dict[str, str] = None
    ) -> Optional[JSON]:
        key = f"{method} {url}"
        bucket = self._buckets_lock.get(key)
        if bucket is None:
            self._buckets_lock[key] = bucket = asyncio.Lock()

        headers = {
            'Authorization': self.__token,
            'Content-Type': 'application/json',
            **headers
        }

        await bucket.acquire()
        if not self._global_ratelimited.is_set():
            await self._global_ratelimited.wait()

        try:
            for remaining in range(self.MAX_RETRIES, 0, -1):
                async with self.__session.request(method, url, params=params, json=data, headers=headers) as response:
                    bucket_remaining = response.headers.get("X-RateLimit-Remaining")
                    if int(bucket_remaining) == 0:
                        await asyncio.sleep(float(response.headers.get("X-RateLimit-Reset-After")))

                    data = await response.json()
                    if 300 > response.status >= 200:
                        return data

                    if 400 <= response.status < 500:
                        if response.status == 429:
                            is_global = data.get("global", False)

                            if is_global:
                                self._global_ratelimited.clear()

                            await asyncio.sleep(float(data.get("retry_after")))

                            if is_global:
                                self._global_ratelimited.set()
                            continue

                        if response.status == 404:
                            raise NotFound(response, json=data)

                        if response.status == 401:
                            raise Unauthorized(response)

                        if response.status == 403:
                            raise Forbidden(response, json=data)

                    if 500 <= response.status < 600:
                        if remaining == 1:
                            raise InternalServerError(response, json=data)

                        continue  # Retry if possible
        finally:
            bucket.release()

    async def close(self) -> None:
        await self.__session.close()
