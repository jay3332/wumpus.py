from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, Iterable, TypeVar

from .connection import Connection
from .user import User

from ..typings import Snowflake


__all__ = (
    'BaseManager',
)


T = TypeVar('T')
C = TypeVar('C', bound='BaseManager')


class BaseManager(Generic[T], ABC):
    def __init__(self, connection: Connection) -> None:
        self._connection: Connection = connection

    @abstractmethod
    def find(self: C, predicate: Callable[[T], bool], /) -> T:
        raise NotImplementedError

    @abstractmethod
    def filter(self: C, predicate: Callable[[T], bool], /) -> Iterable[T]:
        raise NotImplementedError

    @abstractmethod
    def subset(self: C, predicate: Callable[[T], bool], /) -> C:
        raise NotImplementedError


class UserManager(BaseManager[User]):
    def __init__(
        self, 
        connection: Connection,
        /,
        cache: Dict[Snowflake, User] = None,
    ) -> None:
        super().__init__(connection)
        self._cache: Dict[Snowflake, User] = cache or {}

    @property
    def cache(self, /) -> Dict[Snowflake, User]:
        return self._cache

    @property
    def count(self, /) -> int:
        return len(self._cache)

    def get(self, id: Snowflake, /) -> User:
        return self._cache.get(id)

    def find(self, predicate: Callable[[User], bool], /) -> User:
        for sample in self._cache.values():
            if predicate(sample):
                return sample

    def filter(self, predicate: Callable[[User], bool], /) -> User:
        return filter(predicate, self._cache.values()) 

    def subset(self: C, predicate: Callable[[User], bool], /) -> C:
        new_cache = {k: v for k, v in self._cache.items() if predicate(v)}
        return UserManager(self._connection, new_cache)

    def __len__(self, /) -> int:
        return self.count
