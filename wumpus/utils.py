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
