from .connection import Connection
from ..typings import Snowflake
from typing import List, Optional, Union, Any
from .object import Object

class Emoji(Object):
    """
    Represents a custom Emoji.
    
    Attributes
    ----------
    id: :class:`int`
    name: :class:`str`
    roles: List[:class:`int`]
    user: :class:`.User`
    require_colons: :class:`bool`
    managed: :class:`bool`
    animated: :class:`bool`
    available: :class:`bool`


    """
    def __init__(self, connection: Connection, data: ..., /) -> None:
        self._connection = connection
        self._load_data(data)
    
    def _load_data(self, data: ...) -> None:
        self.id: Snowflake = int(data.get('id'))
        self.name: str = data.get('name')
        self.roles: List[Snowflake] = [int(id) for id in data.get('roles')]
        self.user: ... = ... # TODO: User object
        self.require_colons: bool = data.get('require_colons', False)
        self.managed: bool = data.get('managed', False)
        self.animated: bool = data.get('animated', False)
        self.available: bool = data.get('available', True)
        super().__init__(self.id)

    def __str__(self) -> str:
        a = 'a' if not self.animated else ''
        return f'<{a}:{self.name}:{self.id}>'
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Emoji) and other.id == self.id
    
    def __ne__(self, other: Any) -> bool:
        return not self == other

