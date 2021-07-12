from .bitfield import InvertedBitfield, bit

class SystemChannelFlags(InvertedBitfield):
    @bit(1)
    def supress_join_notification(self, /) -> None:
        """
        Whether or not it suppress member join notifications.
        """

    @bit(2)
    def supress_premium_notification(self, /) -> None:
        """
        Whether or not it suppress server boost notifications.
        """

    @bit(4)
    def supress_guild_reminder_notification(self, /) -> None:
        """
        Whether or not to suppress server setup tips.
        """