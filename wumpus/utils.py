from base64 import b64encode
from inspect import isawaitable
from typing import Any, Awaitable, Callable, Union, TypeVar, overload

from .core.objects import deconstruct_snowflake


__all__ = (
    'maybe_coro',
    'deconstruct_snowflake'
)


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
