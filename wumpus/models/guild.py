from datetime import datetime
from typing import List, Optional, TypeVar

from ..core.enums import DefaultMessageNotificationLevel, ExplicitContentFilterLevel, MFALevel, VerificationLevel, GuildNSFWLevel, PremiumTier
from ..core.connection import Connection
from ..typings import Snowflake
from ..typings.payloads import GuildPayload
from .asset import Asset
from .objects import NativeObject
from .role import Role

T = TypeVar('T', bound='Guild')

__all__ = (
    'Guild',
)


class Guild(NativeObject):
    __slots__ = (
        '_name',
    ) + NativeObject.__slots__

    def __init__(self, connection: Connection, /, data: GuildPayload) -> None:
        self._connection: Connection = connection
        self._last_received_data: GuildPayload = {}
        self._load_data(data)
        super().__init__()

    def _load_asset(self, key: str, /, *, data: GuildPayload, entity: str) -> Asset:
        _hash = data.get(key)

        if _hash is not None:
            animated = _hash.startswith('a_')
            return Asset(
                self._connection,
                url=f'{entity}/{self.id}/{_hash}',
                animated=animated,
                hash=_hash
            )
        else:
            return None

    def _load_data(self, data: GuildPayload) -> None:
        self._last_received_data |= data
        self._put_snowflake(data['id'])

        self._name: Optional[str] = data.get('name')
        self._unavailable: Optional[bool] = data.get('unavailable', True)
        self._owner_id: Optional[Snowflake] = int(data.get('owner_id'))

        self._afk_channel_id: Optional[Snowflake] = int(data.get('afk_channel_id'))
        self._afk_timeout: Optional[int] = data.get('afk_timeout')
        
        self._widget_enabled: Optional[bool] = data.get('widget_enabled')
        self._widget_channel_id: Optional[Snowflake] = int(data.get('widget_channel_id'))
        
        self._features: List[str] = data.get('features')
        self._application_id: Optional[Snowflake] = int(data.get('application_id'))

        self._system_channel_id: Optional[Snowflake] = int(data.get('system_channel_id'))
        self._rules_channel_id: Optional[Snowflake] = int(data.get('rules_channel_id'))

        self._created_at: datetime = datetime.fromisoformat(data.get('joined_at'))
        self._large: Optional[bool] = data.get('large')
        self._member_count: Optional[int] = data.get('member_count')

        self._max_presences: Optional[int] = data.get('max_presences')
        self._max_members: Optional[int] = data.get('max_members')

        self._vanity_url_code: Optional[str] = data.get('vanity_url_code')
        self._description: Optional[str] = data.get('description')
        self._premium_subscription_count: Optional[int] = data.get('premium_subscription_count')
        self._preferred_locale: Optional[str] = data.get('preferred_locale')
        self._public_updates_channel_id: Optional[Snowflake] = data.get('public_updates_channel_id')
        self._max_video_channel_users: Optional[int] = data.get('max_video_channel_users')

        self._verification_level: Optional[VerificationLevel] = VerificationLevel(data.get('verification_level'))
        self._default_message_notifications: Optional[DefaultMessageNotificationLevel] = DefaultMessageNotificationLevel(data.get('default_message_notifications'))
        self._explicit_content_filter: Optional[ExplicitContentFilterLevel] = ExplicitContentFilterLevel(data.get('explicit_content_filter'))
        self._mfa_level: Optional[MFALevel] = MFALevel(data.get('mfa_level'))
        self._premium_tier: Optional[PremiumTier] = PremiumTier(data.get('premium_tier'))
        self._nsfw_level: Optional[GuildNSFWLevel] = GuildNSFWLevel(data.get('nsfw_level'))
        # TODO: MemberManager, RoleManager, EmojiManager, etc 

        self.icon: Asset = self._load_asset('icon', data=data, entity='icons')
        self.banner: Asset = self._load_asset('banner', data=data, entity='banners')
        self.splash: Asset = self._load_asset('splash', data=data, entity='splashes')
        self.discovery_splash: Asset = self._load_asset('discovery_splash', data=data, entity='discovery-splashes')

    @property
    def name(self, /) -> str:
        return self._name

    def _copy(self: T) -> T:
        return self.__class__(self._connection, self._last_received_data)

    def __str__(self, /) -> str:
        return self.name

    def __repr__(self, /) -> str:
        return f'<Guild name={self.name!r} id={self.id}>'
