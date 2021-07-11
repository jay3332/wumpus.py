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
