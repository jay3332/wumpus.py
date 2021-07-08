from typing import Literal, Optional, TypedDict
from . import Snowflake


class PartialUserPayload(TypedDict):
    id: Snowflake
    username: str
    discriminator: str
    avatar: Optional[str]
    

class UserPayload(PartialUserPayload, total=False):
    bot: bool
    system: bool
    mfa_enabled: bool
    locale: str
    verified: bool
    email: str
    flags: int
    premium_type: Literal[0, 1, 2]
    public_flags: int
