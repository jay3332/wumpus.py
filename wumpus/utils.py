import time
import asyncio

from asyncio import AbstractEventLoop

from base64 import b64encode
from collections import deque
from inspect import isawaitable
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Optional, 
    TypeVar,
    Union,
    overload
)

from .models.objects import deconstruct_snowflake


__all__ = (
    'maybe_coro',
    'deconstruct_snowflake',
    '_try_int',
    '_get_mimetype',
    '_bytes_to_image_data',
    'Ratelimiter'
)


T = TypeVar('T', bound='Ratelimiter')
RT = TypeVar('RT', bound=Union[Any, Awaitable[Any]])


@overload
def maybe_coro(func: Callable[..., Awaitable[RT]], *args, **kwargs) -> Awaitable[RT]:
    ...


@overload
def maybe_coro(func: Callable[..., RT], *args, **kwargs) -> RT:
    ...


async def maybe_coro(func, *args, **kwargs):
    res = func(*args, **kwargs)
    if isawaitable(res):
        return await res
    
    return res


def _get_mimetype(data: bytes) -> str:
    if data.startswith(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'):
        return 'image/png'
    elif data[0:3] == b'\xff\xd8\xff' or data[6:10] in (b'JFIF', b'Exif'):
        return 'image/jpeg'
    elif data.startswith((b'\x47\x49\x46\x38\x37\x61', b'\x47\x49\x46\x38\x39\x61')):
        return 'image/gif'
    elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return 'image/webp'

    raise ValueError('unsupported image format')


def _bytes_to_image_data(data: bytes) -> str:
    mimetype = _get_mimetype(data)
    result = b64encode(data).decode('ascii')
    return f'data:{mimetype};base64,{result}'


@overload
def _try_int(value: int, /) -> int:
    ...


@overload
def _try_int(value: str, /) -> Optional[int]:
    ...


@overload
def _try_int(value: None, /) -> None:
    ...


def _try_int(value, /):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


class Ratelimiter:
    """
    Utility class used to handle rate-limits.
    """

    def __init__(
        self: T, 
        /,
        rate: int, 
        per: int, 
        *, 
        callback: Optional[Coroutine[None, None, Any]] = None,
        loop: Optional[AbstractEventLoop] = None
    ) -> T:
        self.rate: int = rate
        self.per: int = per
        self.recent_calls: deque = deque()
        self.loop: Optional[AbstractEventLoop] = loop or asyncio.get_event_loop()

        self._callback: Optional[Coroutine[None, None, Any]] = callback
        self._lock: asyncio.Lock = asyncio.Lock()
    
    async def __aenter__(self: T) -> T:
        async with self._lock:
            if not self.loop.is_running:
                raise RuntimeError('Ratelimiter should not be used if event loop is not running')

            if len(self.recent_calls) >= self.rate:
                sleep_until = time.time() + self.per - (self.recent_calls[-1] - self.recent_calls[0])
                if self._callback is not None:
                    self.loop.create_task(self._callback)
                        
                to_sleep = sleep_until - time.time()
                if to_sleep > 0:
                    await asyncio.sleep(to_sleep)
            
            return self

    async def __aexit__(self: T, *_: Any) -> None:
        async with self._lock:
            self.recent_calls.append(time.time())

            # pop the old calls in recent call list.
            while self.recent_calls[-1] - self.recent_calls[0] >= self.per:
                self.recent_calls.popleft() 
