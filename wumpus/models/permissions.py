from .bitfield import Bitfield, bit, bit_alias


class Permissions(Bitfield):
    """Represents the permissions that a member or role has.

    This can be constructed using a permissions integer
    or by using keyword-arguments.
    """

    def __init__(self, value: int = 0, /, **kwargs) -> None:
        super().__init__(value | self._calculate(**kwargs))

    @bit(1)  # 1 << 0
    def create_invites(self, /) -> None:
        ...

    @bit(2)  # 1 << 1
    def kick_members(self, /) -> None:
        ...

    @bit(4)  # 1 << 2
    def ban_members(self, /) -> None:
        ...

    @bit(8)  # 1 << 3
    def administrator(self, /) -> None:
        ...

    @bit(16)  # 1 << 4
    def manage_channels(self, /) -> None:
        ...

    @bit(32)  # 1 << 5
    def manage_guild(self, /) -> None:
        ...

    @bit(64)  # 1 << 6
    def add_reactions(self, /) -> None:
        ...

    @bit(128)  # 1 << 7
    def view_audit_log(self, /) -> None:
        ...

    @bit(256)  # 1 << 8
    def priority_speaker(self, /) -> None:
        ...

    @bit(512)  # 1 << 9
    def stream(self, /) -> None:
        ...

    @bit(1024)  # 1 << 10
    def view_channel(self, /) -> None:
        ...

    @bit_alias(1024)  # 1 << 10
    def read_messages(self, /) -> None:
        ...

    @bit(2048)  # 1 << 11
    def send_messages(self, /) -> None:
        ...

    @bit(4096)  # 1 << 12
    def send_tts_messages(self, /) -> None:
        ...

    @bit(8192)  # 1 << 13
    def manage_messages(self, /) -> None:
        ...

    @bit(16384)  # 1 << 14
    def embed_links(self, /) -> None:
        ...

    @bit(32768)  # 1 << 15
    def attach_files(self, /) -> None:
        ...

    @bit(65536)  # 1 << 16
    def read_message_history(self, /) -> None:
        ...

    @bit_alias(65536)  # 1 << 16
    def view_channel_history(self, /) -> None:
        ...

    @bit(131072)  # 1 << 17
    def mention_everyone(self, /) -> None:
        ...

    @bit(262144)  # 1 << 18
    def use_external_emojis(self, /) -> None:
        ...

    @bit(524288)  # 1 << 19
    def view_guild_insights(self, /) -> None:
        ...

    @bit(1048576)  # 1 << 20
    def connect(self, /) -> None:
        ...

    @bit(2097152)  # 1 << 21
    def speak(self, /) -> None:
        ...

    @bit(4194304)  # 1 << 22
    def mute_members(self, /) -> None:
        ...

    @bit(8388608)  # 1 << 23
    def deafen_members(self, /) -> None:
        ...

    @bit(16777216)  # 1 << 24
    def move_members(self, /) -> None:
        ...

    @bit(33554432)  # 1 << 25
    def use_vad(self, /) -> None:
        ...

    @bit_alias(33554432)  # 1 << 25
    def use_voice_activation(self, /) -> None:
        ...

    @bit(67108864)  # 1 << 26
    def change_nickname(self, /) -> None:
        ...

    @bit(134217728)  # 1 << 27
    def manage_nicknames(self, /) -> None:
        ...

    @bit(268435456)  # 1 << 28
    def manage_roles(self, /) -> None:
        ...

    @bit(536870912)  # 1 << 29
    def manage_webhooks(self, /) -> None:
        ...

    @bit(1073741824)  # 1 << 30
    def manage_emojis(self, /) -> None:
        ...

    @bit(2147483648)  # 1 << 31
    def use_slash_commands(self, /) -> None:
        ...

    @bit(4294967296)  # 1 << 32
    def request_to_speak(self, /) -> None:
        ...

    @bit(17179869184)  # 1 << 34
    def manage_threads(self, /) -> None:
        ...

    @bit(34359738368)  # 1 << 35
    def use_public_threads(self, /) -> None:
        ...

    @bit(68719476736)  # 1 << 36
    def use_private_threads(self, /) -> None:
        ...
