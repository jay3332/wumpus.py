from typing import Type, TypeVar
from .bitfield import Bitfield, bit, bit_alias


T = TypeVar('T', bound='Intents')


class Intents(Bitfield):
    def __init__(self, value: int = 0, /, **kwargs):
        super().__init__(value | self._calculate(**kwargs))

    @bit(1)  # 1 << 0 
    def guilds(self, /) -> None:
        ...

    @bit(2)  # 1 << 1
    def members(self, /) -> None:
        ...

    @bit(4)  # 1 << 2
    def bans(self, /) -> None:
        ...

    @bit(8)  # 1 << 3
    def emojis(self, /) -> None:
        ...

    @bit(16) # 1 << 4
    def integrations(self, /) -> None: 
        ...

    @bit(32)  # 1 << 5
    def webhooks(self, /) -> None:
        ...

    @bit(64)  # 1 << 6
    def invites(self, /) -> None:
        ...

    @bit(128)  # 1 << 7
    def voice(self, /) -> None:
        ...

    @bit(256)  # 1 << 8
    def presences(self, /) -> None:
        ...

    @bit(512)  # 1 << 9
    def guild_messages(self, /) -> None:
        ...

    @bit(1024) # 1 << 10
    def guild_reactions(self, /) -> None:
        ...

    @bit(2048)  # 1 << 11
    def guild_typing(self, /) -> None:
        ...

    @bit(4096)  # 1 << 12
    def dm_messages(self, /) -> None:
        ...

    @bit(8192)  # 1 << 13
    def dm_reactions(self, /) -> None:           
        ...

    @bit(16384)  # 1 << 14
    def dm_typing(self, /) -> None:
        ...

    @bit_alias(4608)  # 1 << 9 | 1 << 12
    def messages(self, /) -> None:
        ...

    @bit_alias(9216)  # 1 << 10 | 1 << 13
    def reactions(self, /) -> None:
        ...

    @bit_alias(18432)  # 1 << 11 | 1 << 14
    def typing(self, /) -> None:
        ...

    @classmethod
    def none(cls: Type[T], /) -> T:
        return cls(0)

    @classmethod
    def all(cls: Type[T], /) -> T:
        return cls(cls.__max_value__)

    @classmethod
    def default(cls: Type[T], /) -> T:
        self = cls.all()
        self.members = False
        self.presences = False
        return self
