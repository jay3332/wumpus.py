from dataclasses import dataclass
from typing import List, Optional

from .objects import Timestamp
from ..typings import JSON

from ..typings.payloads import (
    EmbedPayload,
    EmbedAuthorPayload,
    EmbedFooterPayload,
    EmbedFieldPayload
)


@dataclass
class EmbedField:
    """Represents a field of an :class:`Embed`.

    Attributes
    ----------
    name: str
        The name of the field.
    value: str
        The value of the field.
    inline: bool
        Whether or not this field should be displayed inline.
    """
    
    name: str
    value: str
    inline: bool = True

    def to_json(self, /) -> EmbedFieldPayload:
        return {
            'name': self.name,
            'value': self.value, 
            'inline': self.inline
        }


@dataclass
class EmbedAuthor:
    """Represents the author of an :class:`Embed`.
    
    Attributes
    ----------
    name: str
        The name of the author.
    url: str
        The redirect URL of the author.
    icon_url: str
        The URL of the author's icon.
    """
    
    name: str
    url: str
    icon_url: str
    

@dataclass
class EmbedFooter:
    """Represents the footer of an :class:`Embed`.
    """
    text: str
    icon_url: str
    proxy_icon_url: str


class Embed:
    """Represents a Discord embed.
    
    
    """
    
    def __init__(
        self, 
        json: JSON = None,
        /,
        **fields
    ):
        if json is not None:
            self._from_json(json)

    def _from_json(self, json: EmbedPayload, /) -> None:
        self.title: str = json.get('title')
        self.type: str = json.get('type', 'rich')
        self.description: str = json.get('description')
        self.url: str = json.get('url')

        _timestamp = json.get('timestamp')
        if _timestamp is not None:
            self.timestamp: Optional[Timestamp] = Timestamp.fromisoformat(_timestamp)

        # # TODO: Color class
        self.color: int = json.get('color')

        self.fields: List[EmbedField] = [EmbedField(**field) for field in json.get('fields', [])]

        _author = json.get('author')
        _footer = json.get('footer')

        self.author: Optional[EmbedAuthor] = EmbedAuthor(**_author) if _author is not None else None
        self.footer: Optional[EmbedFooter] = EmbedFooter(**_footer) if _footer is not None else None

        # TODO: The other keys
    
    def to_json(self) -> EmbedPayload:
        embed = {
            'type': self.type or 'rich', 
            'title': self.title, 
            'description': self.description,
            'url': self.url, 
            'timestamp': self.timestamp.isoformat() if self.timestamp is not None else None,
            'color': self.color,
            'author': self.author.to_json()
        }
        