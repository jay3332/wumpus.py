from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, Iterable, TypeVar

from .connection import Connection
from .user import User

from ..errors import NotFound

from ..typings import Snowflake
from ..typings.payloads import PartialUserPayload


__all__ = (
    'BaseManager',
    'UserManager'
)


T = TypeVar('T')
C = TypeVar('C', bound='BaseManager')


class BaseManager(Generic[T], ABC):
    def __init__(self, connection: Connection, /) -> None:
        self._connection: Connection = connection

    def __repr__(self, /) -> str:
        return f'<{self.__class__.__name__}>'

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

    def __repr__(self, /) -> str:
        return f'<{self.__class__.__name__} count={self.count}>'

    def __len__(self, /) -> int:
        return self.count

    @property
    def cache(self, /) -> Dict[Snowflake, User]:
        return self._cache

    @property
    def count(self, /) -> int:
        return len(self._cache)

    def has(self, id: Snowflake, /) -> bool:
        return id in self._cache

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

    def _add_from_payload(self, payload: PartialUserPayload, /) -> User:
        if payload.get('id') is None:
            return  

        # If the ID is already stored in our cache, 
        # then we can just update the cache with the new data.
        if self.has(payload['id']):
            user = self._cache[payload['id']]
            user._load_data(payload)
            return user

        # Otherwise, we need to create a new user object.
        self._cache[user.id] = user = User(self._connection, payload)
        return user

    async def fetch(self, id: Snowflake, /, *, cache: bool = True) -> User:
        """Makes an API request to Discord to fetch a user by their snowflake ID.
        
        Parameters
        ----------
        id: Snowflake
            The user's snowflake ID.
        cache: bool = False
            Whether or not to cache the fetched user.
        
        Returns
        -------
        Optional[:class:`User`]
            The user fetched. If none was found, `None` is returned.
        """
        
        try:
            data = await self._connection.api.users(id).get()
        except NotFound:
            return None

        if cache:
            return self._add_from_payload(data, cache)
        
        _user = User(self._connection, data)
        _user.__object_cached__ = False
        return _user

    async def getch(self, id: Snowflake, /) -> User:
        """Calls :meth:`.UserManager.get` on the given snowflake.
        If no user is found in the cache, :meth:`.UserManager.fetch` 
        is then called instead.

        This is the exact equivalent of doing:

        .. code:: python
            users.get(id) or await users.fetch(id)

        Parameters
        ----------
        id: Snowflake
            The user's snowflake ID.
        
        Returns
        -------
        Optional[:class:`User`]
            The user found. If none was found, `None` is returned.
        """
        
        return self.get(id) or await self.fetch(id)
