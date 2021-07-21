from typing import List, Optional

from .asset import Asset
from .team import Team
from .user import PartialUser
from .objects import NativeObject

from ..core.connection import Connection
from ..typings import Snowflake


class Application(NativeObject):
    """
    Represents a Discord application.

    Attributes
    ----------
    id: :class:`Snowflake` 
        The id of the application
    name: :class:`str` 
        The name of the application
    icon: :class:`~.Asset` 
        The asset of the application
    description: :class:`str` 
        The description of the application
    rpc_origins: Optional[:class:`str`] 
        An optional list of rpc origin urls, if rpc is enabled.
    """

    def __init__(self, connection, data) -> None:
        self._connection: Connection = connection
        self._load_data(data)
        super().__init__()

    def _load_data(self, data) -> None:
        self._put_snowflake(data.get('id'))
        self.name = data.get('name')
        icon = data.get('icon')
        if icon:
            self.cover_image: Asset = Asset(self._connection, url=f"app-icons/{self.id}/{icon}.png", hash=icon)
        self.description: str = data.get('description')
        self.rpc_origins: Optional[List[str]] = data.get('rpc_origins')
        self.bot_public: bool = data.get('bot_public')
        self.bot_require_code_grant: bool = data.get('bot_require_code_grant')
        self.term_of_service_url: Optional[str] = data.get('term_of_service_url')
        self.privacy_policy: Optional[str] = data.get('privacy_policy')
        self.owner: PartialUser = PartialUser(self._connection, data.get('owner'))
        self.summary: str = data.get('summary')
        self.verify_key: str = data.get('verify_key')
        self.team: Team = Team(self._connection, data.get('team'))
        self.guold_id: Optional[Snowflake] = data.get('guold_id')
        self.primary_sku_id: Optional[Snowflake] = data.get('primary_sku_id')
        self.slug: Optional[str] = data.get('slug')
        cover_image = data.get('cover_image')
        if cover_image:
            self.cover_image: Optional[Asset] = Asset(self._connection, url=f"app-icons/{self.id}/{cover_image}.png", hash=cover_image)
        else:
            self.cover_image: Optional[Asset] = None
        # TODO: flags

    def _copy(self, /):
        ...
