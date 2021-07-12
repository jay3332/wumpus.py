from typing import Awaitable, Callable, List, Union

from ... import Client
from ...models import Message


PrefixType = Union[str, List[str], Callable[['Bot', Message], Union[Union[str, List[str]], Awaitable[Union[str, List[str]]]]]]


class Bot(Client):
   def __init__(
        self, 
        /,
        prefix: PrefixType,
        *,
        prefix_case_insensitive: bool = False,
        case_insensitive: bool = False,
        **kwargs
    ):
        self.__prefix: PrefixType = prefix
