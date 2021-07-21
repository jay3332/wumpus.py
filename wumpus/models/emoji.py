from .asset import Asset
from .objects import Object, NativeObject

from ..core.connection import Connection
from ..typings import JSON, Snowflake

from typing import Any, List, Type, TypeVar


PT = TypeVar('PT', bound='PartialEmoji')


__all__ = (
    'PartialEmoji',
    'Emoji'
)


class PartialEmoji(Object):
    """Represents an emoji with basic attributes.
    
    Attributes
    ----------
    name: str
        The name of this emoji.
    id: Optional[int]
        The snowflake ID of this emoji.
    animated: bool
        Whether or not this emoji is animated.
    """

    def __init__(
        self, 
        /, 
        *, 
        name: str,
        id: Snowflake = None,
        animated: bool = False,
        connection: Connection = None
    ) -> None:
        super().__init__(id)

        self.name: str = name
        self.animated: bool = animated 
        self._asset: Asset = None

        self._connection: Connection = connection

    @classmethod
    def parse(cls: Type[PT], string: str, /, *, connection: Connection = None) -> PT:
        """Parses a string that represents an emoji into a :class:`~.PartialEmoji`.

        The given string should follow one of the following formats:

        * `<:name:id>`
        * `<a:name:id>`
        * `name:id`
        * `a:name:id`

        .. note:: This does not account for unicode emoji. (It is been considered, however)

        Parameters
        ----------
        string: str
            The string to parse.

        Returns
        -------
        :class:`~.PartialEmoji`
            The partial emoji object representing the string.
        """

        animated = False
        string = string.strip('<> ')
        if string.startswith('a:'):
            animated = True
            string = string[2:]

        try:
            name, id = string.strip(':').split(':')
        except ValueError:
            raise ValueError('invalid emoji given')
            
        return cls(name=name, id=int(id), animated=animated, connection=connection)

    @property
    def image(self) -> Asset:
        """Retrieves the :class:`~.Asset` that represents this emoji.

        Returns
        -------
        :class:`~.Asset`
            The asset of this emoji.

        Raises
        ------
        ValueError
            This asset is a unicode emoji.
        """

        if self.is_unicode():
            raise ValueError('cannot retrieve assets of unicode emoji')

        if self._asset:
            return self._asset

        self._asset = res = Asset(
            self._connection, 
            url=f'emojis/{self.id}',
            animated=self.animated
        )

        return res

    @property
    def url(self) -> str:
        """
        str: The asset URL of this image.
        """
        return self.image.url

    def is_unicode(self, /) -> bool:
        """Return whether or not this asset is a unicode emoji.

        Returns
        -------
        bool
            Whether or not this asset is a unicode emoji.
        """
        return self.id is None

    def to_json(self, /) -> JSON:
        """Turns this into a raw JSON payload to be sent to Discord.

        This only takes into account minimal attributes as they are all we need.

        Returns
        -------
        dict
            The payload that was made.
        """

        return {
            'name': self.name,
            'id': self.id,
            'animated': self.animated
        }

    @classmethod
    def from_json(cls: Type[PT], payload: JSON, /, *, connection: Connection = None) -> PT:
        """Generates a :class:`~.PartialEmoji` from a raw JSON payload.
        
        Parameters
        ----------
        payload: dict
            The payload to use.

        Returns
        -------
        :class:`~.PartialEmoji`
            The generated partial emoji object from the payload.
        """

        return cls(
            name=payload['name'],
            id=payload.get('id'),
            animated=payload.get('animated', False),
            connection=connection
        )

    def _to_route(self, /) -> str:
        if not self.id:
            return self.name

        return f'{self.name}:{self.id}'

    def __str__(self, /) -> str:
        if self.is_unicode():
            return self.name

        a = 'a' if self.animated else ''
        return f'<{a}:{self.name}:{self.id}>'

    def __repr__(self, /) -> str:
        return f'<{self.__class__.__name__} name={self.name!r} id={self.id} animated={self.animated}>'


class Emoji(NativeObject):
    """
    Represents a custom Emoji.
    
    Attributes
    ----------
    id: int
        The snowflake ID of this emoji.
    name: str
        The name of this emoji.
    roles: List[:class:`int`]
    user: :class:`~.User`
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

