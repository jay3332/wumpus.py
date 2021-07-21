from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, List, Iterable, TypeVar

from .connection import Connection

from ..errors import NotFound

from ..models.user import User
from ..models.guild import Guild

from ..typings import Snowflake
from ..typings.payloads import PartialUserPayload, GuildPayload


__all__ = (
    'BaseManager',
    'UserManager',
    'GuildManager'
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


class CacheBasedManager(BaseManager[T], Generic[T]):
    def __init__(
        self, 
        connection: Connection,
        /,
        cache: Dict[Snowflake, User] = None,
    ) -> None:
        super().__init__(connection)
        self._cache: Dict[Snowflake, T] = cache or {}
    
    def __repr__(self, /) -> str:
        return f'<{self.__class__.__name__} count={self.count}>'

    def __len__(self, /) -> int:
        return self.count

    def __iter__(self, /) -> Iterable[T]:
        return iter(self._cache.values())

    @property
    def cache(self, /) -> Dict[Snowflake, T]:
        """Dict[Snowflake, Any]: The internal cache of this manager."""
        return self._cache

    @property
    def count(self, /) -> int:
        """int: The amount of objects stored in the internal cache."""
        return len(self._cache)

    def flatten(self, /) -> List[T]:
        """Returns a list of all objects stored in the internal cache.

        Returns
        -------
        List[Any]
        """
        return list(self._cache.values())

    def has(self, id: Snowflake, /) -> bool:
        """Return whether or not the internal cache is storing
        an object mapped to the specified snowflake ID.

        Parameters
        ----------
        id: Snowflake
            The ID to lookup.

        Returns
        -------
        bool
        """
        return id in self._cache

    def get(self, id: Snowflake, /) -> T:
        """Gets and returns an item from the internal cache by it's snowflake ID.

        Parameters
        ----------
        id: Snowflake
            The ID to lookup.
        """
        return self._cache.get(id)

    def find(self, predicate: Callable[[T], bool], /) -> T:
        """Finds an item in the internal cache by a predicate function.

        Parameters
        ----------
        predicate: Callable[[Any], bool]
            The check predicate to use.

        Returns
        -------
        Optional[Any]
        """
        for sample in self._cache.values():
            if predicate(sample):
                return sample

    def filter(self, predicate: Callable[[T], bool], /) -> Iterable[T]:
        """Returns a :py:class:`filter` object after filtering the internal class with a predicate.

        Parameters
        ----------
        predicate: Callable[[Any], bool]
            The check predicate to use.

        Returns
        -------
        Iterable[Any]
        """
        return filter(predicate, self._cache.values()) 

    def subset(self: C, predicate: Callable[[T], bool], /) -> C:
        """Creates a copy of this class with a subset of the cache.

        For example, `Manager([1, 2, 3]).subset(lambda x: x % 2 == 1)` would return
        `Manager([1, 3])`. (Note that this is not how managers are actually constructed.)

        Parameters
        ----------
        predicate: Callable[[Any], bool]
            The check predicate to use.

        Returns
        -------
        Any
        """
        new_cache = {k: v for k, v in self._cache.items() if predicate(v)}
        return self.__class__(self._connection, new_cache)


class UserManager(CacheBasedManager[User]):
    def _add_from_payload(self, payload: PartialUserPayload, /) -> User:
        if payload.get('id') is None:
            return  

        snowflake = int(payload['id'])

        # If the ID is already stored in our cache, 
        # then we can just update the cache with the new data.
        if self.has(snowflake):
            user = self._cache[snowflake]
            user._load_data(payload)
            return user

        # Otherwise, we need to create a new user object.
        self._cache[snowflake] = user = User(self._connection, payload)
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
        Optional[:class:`.User`]
            The user fetched. If none was found, `None` is returned.
        """
        
        try:
            data = await self._connection.api.users(id).get()
        except NotFound:
            return None

        if cache:
            return self._add_from_payload(data)
        
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
        Optional[:class:`.User`]
            The user found. If none was found, `None` is returned.
        """
        
        return self.get(id) or await self.fetch(id)


class GuildManager(CacheBasedManager[Guild]):
    def _add_from_payload(self, payload: GuildPayload, /) -> Guild:
        if payload.get('id') is None:
            return  

        snowflake = int(payload['id'])

        # If the ID is already stored in our cache, 
        # then we can just update the cache with the new data.
        if self.has(snowflake):
            guild = self._cache[snowflake]
            guild._load_data(payload)
            return guild

        # Otherwise, we need to create a new guild object.
        self._cache[snowflake] = guild = Guild(self._connection, payload)
        return guild

    async def fetch(self, id: Snowflake, /, *, cache: bool = True) -> GuildPayload:
        """Makes an API request to Discord to fetch a guild by it's snowflake ID.
        
        Parameters
        ----------
        id: Snowflake
            The guild's snowflake ID.
        cache: bool = False
            Whether or not to cache the fetched guild.
        
        Returns
        -------
        Optional[:class:`.Guild`]
            The guild fetched. If none was found, `None` is returned.
        """
        
        try:
            data = await self._connection.api.guilds(id).get({'with_counts': True})
        except NotFound:
            return None

        if cache:
            return self._add_from_payload(data)
        
        _guild = Guild(self._connection, data)
        _guild.__object_cached__ = False
        return _guild

    async def getch(self, id: Snowflake, /) -> User:
        """Calls :meth:`.GuildManager.get` on the given snowflake.
        If no user is found in the cache, :meth:`.GuildManager.fetch` 
        is then called instead.

        This is the exact equivalent of doing:

        .. code:: python
            guilds.get(id) or await guilds.fetch(id)

        Parameters
        ----------
        id: Snowflake
            The guild's snowflake ID.
        
        Returns
        -------
        Optional[:class:`.Guild`]
            The guild found. If none was found, `None` is returned.
        """

        return self.get(id) or await self.fetch(id)
