from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, TypeVar

from .connection import Connection


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
    def subset(self: C, predicate: Callable[[T], bool], /) -> C[T]:
        raise NotImplementedError
