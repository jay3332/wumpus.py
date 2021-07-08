from aiohttp import ClientResponse
from .typings import JSON


__all__ = (
    'WumpusError',
    'HTTPError',
    'Unauthorized',
    'NotFound',
    'Forbidden',
    'InternalServerError'
)


class WumpusError(Exception):
    """
    The base :class`Exception` that all errors related to this library inherit from.
    This can techinically be used to handle all errors raised by by this library.
    """


class HTTPError(WumpusError):
    """
    Something unexpected happened when trying to make a request.
    """

    def __init__(self, response: ClientResponse, /, *, json: JSON = None, message: str = None) -> None:
        self.status: int = response.status
        self.response: ClientResponse = response
        self.code: int = 0

        _message = None
        if isinstance(json, dict):
            _message = json.get('message', None)
            self.code = _message.get('code', 0)

        elif message is not None:
            _message = message

        self.message: str = _message or 'Unknown error when trying to request from Discord.'
        super().__init__("{0.status} {0.response.reason}: {0.message}".format(self))


class Forbidden(HTTPError):
    """
    Raised when you are missing permissions for a certain action.
    """

    # status: 403


class Unauthorized(HTTPError):
    """
    You are not authorized,
    this should only be raised when you regenerate your token during runtime.
    """

    # status: 401

    MESSAGE = "You are not authorized, this should only be raised if you regenerated your token during runtime."

    def __init__(self, response: ClientResponse, /) -> None:
        super().__init__(response, message=self.MESSAGE)


class NotFound(HTTPError):
    """
    What you requested for is not found.
    """

    # status: 404


class InternalServerError(HTTPError):
    """
    Something went wrong inside of Discord, internally.
    """

    # status: 500
