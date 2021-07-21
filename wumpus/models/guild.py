from typing import List, Optional, TypeVar

from ..core.enums import (
    MFALevel, 
    PremiumTier,
    GuildNSFWLevel, 
    VerificationLevel, 
    ExplicitContentFilterLevel, 
    DefaultMessageNotificationLevel,
    GuildFeature
)

from ..core.connection import Connection
from ..core.http import Router

from ..typings import Snowflake, ValidDeleteMessageDays
from ..typings.payloads import GuildPayload, GuildPreviewPayload

from .member import Member
from .bitfield import InvertedBitfield, bit
from .objects import Object, NativeObject, Timestamp
from .asset import Asset

from ..utils import _try_int, _bytes_to_image_data


T = TypeVar('T', bound='GuildPreview')

__all__ = (
    'SystemChannelFlags',
    'Guild',
    'GuildPreview'
)


class SystemChannelFlags(InvertedBitfield):
    @bit(1)
    def suppress_join_notifications(self, /) -> None:
        """
        Whether or not to suppress join notifications.
        """

    @bit(2)
    def suppress_premium_notifications(self, /) -> None:
        """
        Whether or not to suppress server boost notifications.
        """

    @bit(4)
    def suppress_guild_reminder_notifications(self, /) -> None:
        """
        Whether or not to suppress server setup tips.
        """


# noinspection PyTypedDict
class GuildPreview(NativeObject):
    __slots__ = (
        '_name',
        '_emojis',
        '_features',
        '_member_count',
        '_presence_count',
        '_features',
        '_description',
        'icon',
        'splash',
        'discovery_splash'
    ) + NativeObject.__slots__

    def __init__(self, connection: Connection, /, data: GuildPreviewPayload) -> None:
        self._connection: Connection = connection
        self._last_received_data: GuildPreviewPayload = {}
        self._load_data(data)
        super().__init__()

    def _load_asset(self, key: str, /, *, data: GuildPreviewPayload, entity: str) -> Asset:
        _hash = data.get(key)

        if _hash is None:
            return

        animated = _hash.startswith('a_')
        return Asset(
            self._connection,
            url=f'{entity}/{self.id}/{_hash}',
            animated=animated,
            hash=_hash
        )

    def _load_data(self, data: GuildPayload) -> None:
        self._last_received_data |= data
        self._put_snowflake(data['id'])

        self._name: Optional[str] = data.get('name')
        self._features: List[GuildFeature] = [GuildFeature(feature) for feature in data.get('features', [])]
        self._description: Optional[str] = data.get('description')

        self.icon: Optional[Asset] = self._load_asset('icon', data=data, entity='icons')
        self.splash: Optional[Asset] = self._load_asset('splash', data=data, entity='splashes')
        self.discovery_splash: Optional[Asset] = self._load_asset('discovery_splash', data=data, entity='discovery-splashes')

    @property
    def name(self, /) -> Optional[str]:
        return self._name

    @property
    def features(self, /) -> List[GuildFeature]:
        return self._features

    @property
    def description(self, /) -> Optional[str]:
        return self._description

    def _copy(self: T) -> T:
        return self.__class__(self._connection, self._last_received_data)

    def __str__(self, /) -> str:
        return self.name

    def __repr__(self, /) -> str:
        return f'<Guild name={self.name!r} id={self.id}>'


class Guild(GuildPreview):
    __slots__ = (
        '_unavailable',
        '_owner_id',
        '_afk_channel_id',
        '_afk_timeout',
        '_widget_enabled',
        '_widget_channel_id',
        '_application_id',
        '_system_channel_id',
        '_system_channel_flags',
        '_rules_channel_id',
        '_joined_at',
        '_large',
        '_member_count',
        '_max_presences',
        '_max_members',
        '_explicit_content_filter',
        '_vanity_url_code',
        '_premium_subscription_count',
        '_preferred_locale',
        '_public_updates_channel_id',
        '_max_video_channel_users',
        '_verification_level',
        '_default_channel_notifications',
        '_explicit_content_filter',
        '_mfa_level',
        '_premium_tier',
        '_nsfw_level',
        'banner',
    ) + GuildPreview.__slots__

    def __init__(self, connection: Connection, /, data: GuildPayload) -> None:
        super().__init__(connection, data=data)

    def _load_data(self, data: GuildPayload) -> None:
        super()._load_data(data)

        self._unavailable: Optional[bool] = data.get('unavailable', False)
        self._owner_id: Optional[Snowflake] = _try_int(data.get('owner_id'))

        self._afk_channel_id: Optional[Snowflake] = _try_int(data.get('afk_channel_id'))
        self._afk_timeout: Optional[int] = data.get('afk_timeout')
        
        self._widget_enabled: Optional[bool] = data.get('widget_enabled')
        self._widget_channel_id: Optional[Snowflake] = _try_int(data.get('widget_channel_id'))
        
        self._features: Optional[List[str]] = data.get('features')
        self._application_id: Optional[Snowflake] = _try_int(data.get('application_id'))

        self._system_channel_id: Optional[Snowflake] = _try_int(data.get('system_channel_id'))
        self._system_channel_flags: Optional[SystemChannelFlags] = SystemChannelFlags(data.get('system_channel_flags', 0)) 
        self._rules_channel_id: Optional[Snowflake] = _try_int(data.get('rules_channel_id'))

        self._joined_at: Optional[Timestamp] = Timestamp.fromisoformat(data.get('joined_at'))
        self._large: Optional[bool] = data.get('large')
        self._member_count: Optional[int] = data.get('member_count')

        self._max_presences: Optional[int] = data.get('max_presences')
        self._max_members: Optional[int] = data.get('max_members')

        self._vanity_url_code: Optional[str] = data.get('vanity_url_code')
        self._premium_subscription_count: Optional[int] = data.get('premium_subscription_count')
        self._preferred_locale: Optional[str] = data.get('preferred_locale')
        self._public_updates_channel_id: Optional[Snowflake] = data.get('public_updates_channel_id')
        self._max_video_channel_users: Optional[int] = data.get('max_video_channel_users')

        self._verification_level: Optional[VerificationLevel] = VerificationLevel(data.get('verification_level', 0))
        self._default_message_notifications: Optional[DefaultMessageNotificationLevel] = DefaultMessageNotificationLevel(data.get('default_message_notifications', 0))
        self._explicit_content_filter: Optional[ExplicitContentFilterLevel] = ExplicitContentFilterLevel(data.get('explicit_content_filter', 0))
        self._mfa_level: Optional[MFALevel] = MFALevel(data.get('mfa_level', 0))
        self._premium_tier: Optional[PremiumTier] = PremiumTier(data.get('premium_tier', 0))
        self._nsfw_level: Optional[GuildNSFWLevel] = GuildNSFWLevel(data.get('nsfw_level', 0))
        # TODO: MemberManager, RoleManager, EmojiManager, etc 

        self.banner: Optional[Asset] = self._load_asset('banner', data=data, entity='banners')
    
    @property
    def unavailable(self, /) -> bool:
        return self._unavailable
    
    @property
    def owner_id(self, /) -> Optional[Snowflake]:
        return self._owner_id
    
    @property
    def afk_channel_id(self, /) -> Optional[Snowflake]:
        return self._afk_channel_id
    
    @property
    def afk_timeout(self, /) -> Optional[int]:
        return self._afk_timeout
    
    @property
    def widget_enabled(self, /) -> bool:
        return self._widget_enabled
    
    @property
    def widget_channel_id(self, /) -> Optional[Snowflake]:
        return self._widget_channel_id

    @property
    def application_id(self, /) -> Optional[Snowflake]:
        return self._application_id
    
    @property
    def system_channel_id(self, /) -> Optional[Snowflake]:
        return self._system_channel_id
    
    @property
    def system_channel_flags(self, /) -> Optional[SystemChannelFlags]:
        return self._system_channel_flags
    
    @property
    def rules_channel_id(self, /) -> Optional[Snowflake]:
        return self._rules_channel_id
    
    @property
    def created_at(self, /) -> Optional[Timestamp]:
        return self._joined_at

    @property
    def large(self, /) -> Optional[bool]:
        return self._large
    
    @property
    def member_count(self, /) -> Optional[int]:
        return self._member_count
    
    @property
    def max_presences(self, /) -> Optional[int]:
        return self._max_presences
    
    @property
    def max_members(self, /) -> Optional[int]:
        return self._max_members
    
    @property
    def vanity_url_code(self, /) -> Optional[str]:
        return self._vanity_url_code
    
    @property
    def premium_subscription_count(self, /) -> Optional[int]:
        return self._premium_subscription_count

    @property
    def preferred_locale(self, /) -> Optional[str]:
        return self._preferred_locale

    @property
    def public_updates_channel_id(self, /) -> Optional[Snowflake]:
        return self._public_updates_channel_id

    @property
    def max_video_channel_users(self, /) -> Optional[int]:
        return self._max_video_channel_users

    @property
    def verification_level(self, /) -> Optional[VerificationLevel]:
        return self._verification_level
    
    @property
    def default_message_notifications(self, /) -> Optional[DefaultMessageNotificationLevel]:
        return self._default_message_notifications
    
    @property
    def explicit_content_filter(self, /) -> Optional[ExplicitContentFilterLevel]:
        return self._explicit_content_filter
    
    @property
    def mfa_level(self, /) -> Optional[MFALevel]:
        return self._mfa_level
    
    @property
    def premium_tier(self, /) -> Optional[PremiumTier]:
        return self._premium_tier
    
    @property
    def nsfw_level(self, /) -> Optional[GuildNSFWLevel]:
        return self._nsfw_level

    @property
    def _api(self, /) -> Router:
        return self._connection.api.guilds(self.id)

    async def kick(self: T, member: Member, *, reason: str = None) -> None:
        await self._api.members(member.id).delete(reason=reason)
    
    async def ban(self: T, member: Member, *, reason: str = None, delete_message_days: ValidDeleteMessageDays = 1) -> None:
        await self._api.bans(member.id).put({'delete_message_days': delete_message_days}, reason=reason)

    async def unban(self: T, member: Object, *, reason: str = None) -> None:
        await self._api.bans(member.id).delete(reason=reason)

    async def leave(self, /) -> None:
        await self._connection.api.users.me.guilds.delete()

    async def delete(self, /) -> None:
        await self._api.delete()

    async def edit(
        self,
        /,
        *,
        name: str = None,
        verification_level: VerificationLevel = ...,
        icon: bytes = None,
        reason: str = None
        # TODO: Implement rest
    ) -> None:
        payload = {}

        if name is not None:
            payload['name'] = name

        if verification_level is not None:
            payload['verification_level'] = verification_level.value

        if icon is not ...:
            if isinstance(icon, str):
                with open(icon, 'rb') as fp:
                    icon = fp.read()

            if isinstance(icon, bytes):
                icon = _bytes_to_image_data(icon)

            payload['icon'] = icon

        await self._api.patch(payload, reason=reason)
