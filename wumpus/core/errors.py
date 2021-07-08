__all__ = ("WumpusError", "HTTPError", "Unauthorized", "NotFound", "InternalServerError")


class WumpusError(Exception):
    """
    The base :class`Exception` that all Wumpus's errors inherited from.
    So theoretically you can use this to handle all exceptions by wumpus.
    """


class HTTPError(WumpusError):
    """"""

    def __init__(self, code, message, /):
        self.code = code
        self.message = message
        super().__init__(f"{self.code}: {self.message}")


class Forbidden(HTTPError):
    """
    You do not have permission to do that.
    """

    def __init__(self):
        super().__init__(403, "You do not have permission to do that")


class Unauthorized(HTTPError):
    """
    You are not authorized,
    this should only be raised when you regenerated your token during runtime.
    """

    def __init__(self):
        super().__init__(
            401, "You are not authorized, this should only be raised when you regenerated your token during runtime."
        )


class NotFound(HTTPError):
    """
    What you requested for is not found.
    """

    def __init__(self):
        super().__init__(404, "What you requested for is not found")


class InternalServerError(HTTPError):
    """
    Something went wrong inside Discord.
    """

    def __init__(self):
        super().__init__(500, "Something went wrong inside Discord")
