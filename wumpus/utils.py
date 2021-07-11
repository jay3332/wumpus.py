import asyncio
import time
from base64 import b64encode
from collections import deque
from inspect import isawaitable
from typing import (Any, Awaitable, Callable, Coroutine, Optional, TypeVar,
                    Union, overload)

from .core.objects import deconstruct_snowflake

__all__ = (
    'maybe_coro',
    'deconstruct_snowflake'
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


class Ratelimiter:
    """
    A ratelimiter mainly used for gateway ratelimit.
    """
    def __init__(self: T, max_calls: int, period: int, callback: Optional[Coroutine[Any]] = None) -> T:
        self.max_calls: int = max_calls
        self.period: int = period
        self._callback: Optional[Coroutine[Any]] = callback

        self.recent_calls: deque = deque()
        self._lock: asyncio.Lock = asyncio.Lock()
    
    async def __aenter__(self: T) -> T:
        async with self._lock:
            loop = asyncio.get_event_loop()
            if not loop.is_running():
                raise RuntimeError('Ratelimiter should not be used if event loop is not running')

            if len(self.recent_calls) >= self.max_calls:
                sleep_until = time.time() + self.period - (self.recent_calls[-1] - self.recent_calls[0])
                if self._callback is not None:
                    loop.create_task(self._callback)
                        
                to_sleep = sleep_until - time.time()
                if to_sleep > 0:
                    await asyncio.sleep(to_sleep)
            
            return self

    async def __aexit__(self: T, *args: Any, **kwargs: Any) -> None:
        async with self._lock:
            self.recent_calls.append(time.time())

            # pop the old calls in recent call list. 
            # not sure if this is the best way to do it but hm.
            while (self.recent_calls[-1] - self.recent_calls[0]) >= self.period:
                self.recent_calls.popleft() # This is why I used deque because del self.recent_calls[0] is nono pog. 
