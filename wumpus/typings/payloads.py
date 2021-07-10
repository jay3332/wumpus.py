from __future__ import annotations

from typing import List, Literal, Optional, TypedDict
from . import Snowflake, JSON


class ReadyEventPayload(TypedDict, total=False):
    v: int
    user: UserPayload
    guilds: List[UnavailableGuildPayload]
    session_id: str
    shard: List[int]
    application: JSON


class PartialUserPayload(TypedDict, total=False):
    id: Snowflake
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: bool
    system: bool
    public_flags: int


class UserPayload(PartialUserPayload, total=False):
    mfa_enabled: bool
    locale: str
    verified: bool
    email: str
    flags: int
    premium_type: Literal[0, 1, 2]


class UnavailableGuildPayload(TypedDict, total=False):
    id: Snowflake
    unavailable: bool


class GuildPreviewPayload(UnavailableGuildPayload):
    name: str
    icon: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    emojis: List[JSON]  # TODO: Emoji payload
    features: List[str]  # maybe use Literal here
    description: Optional[str]


class PartialGuildPayload(GuildPreviewPayload):
    owner_id: Snowflake
    afk_channel_id: Optional[Snowflake]
    afk_timeout: int
    verification_level: Literal[0, 1, 2, 3, 4]
    default_message_notifications: Literal[0, 1]
    explicit_content_filter: Literal[0, 1, 2]
    roles: List[JSON]  # TODO: Role payload
    mfa_level: Literal[0, 1]
    nsfw_level: Literal[0, 1, 2, 3]
    application_id: Optional[Snowflake]
    system_channel_id: Optional[Snowflake]
    system_channel_flags: int
    rules_channel_id: Optional[Snowflake]
    vanity_url_code: Optional[str]
    banner: Optional[str]
    premium_tier: Literal[0, 1, 2, 3]
    preferred_locale: str
    public_updates_channel_id: Optional[Snowflake]


class GuildPayload(PartialGuildPayload, total=False):
    region: Optional[str]  # will be removed in v9 (replaced by rtc_region)
    icon_hash: Optional[str]
    owner: bool
    permissions: str
    widget_enabled: bool
    widget_channel_id: Optional[Snowflake]
    joined_at: Optional[str]
    large: bool
    member_count: int
    voice_states: List[JSON]
    members: List[JSON]  # TODO: Member payload
    channels: List[JSON]  # TODO: [Guild]Channel payload
    presences: List[JSON]
    threads: List[JSON]
    max_presences: Optional[int]
    max_members: int
    premium_subscription_count: int
    max_video_channel_users: int


class EmbedAuthorPayload(TypedDict, total=False):
    name: str
    url: Optional[str]
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]


class EmbedFooterPayload(TypedDict, total=False):
    text: str
    icon_url: Optional[str]
    proxy_icon_url: Optional[str]


class EmbedFieldPayload(TypedDict, total=False):
    name: str
    value: str
    inline: bool


class EmbedImagePayload(TypedDict, total=False):
    url: str
    proxy_url: Optional[str]
    height: int
    width: int


class EmbedThumbnailPayload(TypedDict, total=False):
    url: str       
    proxy_url: Optional[str]
    height: int
    width: int


class EmbedVideoPayload(TypedDict, total=False):
    url: str
    height: int
    width: int
    proxy_url: str


class EmbedProviderPayload(TypedDict, total=False):
    name: str
    url: Optional[str]


class EmbedPayload(TypedDict, total=False):
    title: str
    description: str
    url: str
    timestamp: str
    color: int
    
    author: EmbedAuthorPayload
    footer: EmbedFooterPayload
    image: EmbedImagePayload
    thumbnail: EmbedThumbnailPayload
    video: EmbedVideoPayload
    provider: EmbedProviderPayload
    fields: List[EmbedFieldPayload]
