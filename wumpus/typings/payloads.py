from typing import Literal, Optional, TypedDict
from . import Snowflake


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
