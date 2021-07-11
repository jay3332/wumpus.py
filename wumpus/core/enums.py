from enum import Enum


__all__ = (
    'OpCode',
    'PremiumType'
)


class OpCode(Enum):
    DISPATCH           = 0
    HEARTBEAT          = 1
    IDENTIFY           = 2
    PRESENCE           = 3
    VOICE_STATE        = 4
    VOICE_PING         = 5
    RESUME             = 6
    RECONNECT          = 7
    REQUEST_MEMBERS    = 8
    INVALIDATE_SESSION = 9
    HELLO              = 10
    HEARTBEAT_ACK      = 11


class PremiumType(Enum):
    NONE          = 0
    NITRO_CLASSIC = 1
    NITRO         = 2

    # Aliases
    CLASSIC       = 1
    NITRO_REGULAR = 2


class MemberShipState(Enum):
    INVITED  = 1
    ACCEPTED = 2


class DefaultMessageNotificationLevel(Enum):
    ALL_MESSAGES  = 0
    ONLY_MENTIONS = 1


class ExplicitContentFilterLevel(Enum):
    DISABLED              = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS           = 2


class MFALevel(Enum):
    NONE = 1
    ELEVATED = 2


class VerificationLevel(Enum):
    NONE      = 0
    LOW       = 1
    MEDIUM    = 2
    HIGH      = 3
    VERY_HIGH = 4


class GuildNSFWLevel(Enum):
    DEFAULT        = 0
    EXPLICIT       = 1
    SAFE           = 2
    AGE_RESTRICTED = 3


class PremiumTier(Enum):
    NONE   = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3

