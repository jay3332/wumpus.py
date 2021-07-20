from enum import Enum


__all__ = (
    'OpCode',
    'PremiumType',
    'DefaultMessageNotificationLevel',
    'MFALevel',
    'VerificationLevel',
    'GuildNSFWLevel',
    'PremiumTier',
    'GuildFeature',
    'ExplicitContentFilterLevel',
    'MemberShipState'
)


class OpCode(Enum):
    dispatch           = 0
    heartbeat          = 1
    identify           = 2
    presence           = 3
    voice_state        = 4
    voice_ping         = 5
    resume             = 6
    reconnect          = 7
    request_members    = 8
    invalidate_session = 9
    hello              = 10
    heartbeat_ack      = 11


class PremiumType(Enum):
    """|enum|

    Represents the type of Nitro subscription
    a user has.

    Attributes
    ----------
    none
        The user does not have Nitro.
    nitro_classic
        The user has Nitro Classic.
    nitro
        The user has Nitro.
    """

    none          = 0
    nitro_classic = 1
    nitro         = 2

    # Aliases
    classic       = 1
    nitro_regular = 2


class MemberShipState(Enum):
    invited  = 1
    accepted = 2


class DefaultMessageNotificationLevel(Enum):
    all_messages  = 0
    only_mentions = 1


class ExplicitContentFilterLevel(Enum):
    disabled              = 0
    members_without_roles = 1
    all_members           = 2


class MFALevel(Enum):
    none = 1
    elevated = 2


class VerificationLevel(Enum):
    none      = 0
    low       = 1
    medium    = 2
    high      = 3
    very_high = 4


class GuildNSFWLevel(Enum):
    default        = 0
    explicit       = 1
    safe           = 2
    age_restricted = 3


class PremiumTier(Enum):
    none   = 0
    tier_1 = 1
    tier_2 = 2
    tier_3 = 3


class InviteTargetTypes(Enum):
    stream               = 1
    embedded_application = 2


class GuildFeature(Enum):
    """|enum|

    Represents a key feature a guild has.

    Attributes
    ----------
    animated_icon
        Guild has access to set an animated guild icon.
    banner
        Guild has access to set a guild banner image.
    commerce
        Guild has access to use commerce features (i.e. create store channels).
    community
        Guild can enable welcome screen, Membership Screening, stage channels and discovery, and receives community updates.
    discoverable
        Guild is able to be discovered in the directory.
    featurable
        Guild is able to be featured in the directory.
    invite_splash
        Guild has access to set an invite splash background.
    member_verification_gate
        Guild has enabled Membership Screening.
    news
        Guild has access to create news channels.
    partnered
        Guild is partnered.
    preview_enabled
        Guild can be previewed before joining via Membership Screening or the directory.
    vanity_url
        Guild has access to set a vanity URL.
    verified
        Guild is verified.
    vip_regions
        Guild has access to set 384kbps bitrate in voice (previously VIP voice servers).
    welcome_screen_enabled
        Guild has enabled the welcome screen.
    ticketed_events_enabled
        Guild has enabled ticketed events.
    monetization_enabled
        Guild has enabled monetization.
    more_stickers
        Guild has increased custom sticker slots.
    three_day_thread_archive
        Guild has access to the three day archive time for threads.
    seven_day_thread_archive
        Guild has access to the seven day archive time for threads.
    private_threads
        Guild has access to create private threads.
    """

    animated_icon            = 'ANIMATED_ICON'
    banner                   = 'BANNER'
    commerce                 = 'COMMERCE'
    community                = 'COMMUNITY'
    discoverable             = 'DISCOVERABLE'
    featurable               = 'FEATURABLE'
    invite_splash            = 'INVITE_SPLASH'
    member_verification_gate  = 'MEMBER_VERIFICATION_GATE_ENABLED'
    news                     = 'NEWS'
    partnered                = 'PARTNERED'
    preview_enabled          = 'PREVIEW_ENABLED'
    vanity_url               = 'VANITY_URL'
    verified                  = 'VERIFIED'
    vip_regions              = 'VIP_REGIONS'
    welcome_screen_enabled   = 'WELCOME_SCREEN_ENABLED'
    ticketed_events_enabled  = 'TICKETED_EVENTS_ENABLED'
    monetization_enabled     = 'MONETIZATION_ENABLED'
    more_stickers            = 'MORE_STICKERS'
    three_day_thread_archive = 'THREE_DAY_THREAD_ARCHIVE'
    seven_day_thread_archive = 'SEVEN_DAY_THREAD_ARCHIVE'
    private_threads          = 'PRIVATE_THREADS'
