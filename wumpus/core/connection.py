import re

from asyncio import AbstractEventLoop

from .http import HTTPClient, Router
from .user import ClientUser

from ..typings.payloads import UserPayload


__all__ = (
    'Connection',
)


class Connection:
    __slots__ = ('_loop', '_http', '_ws', '_user', '__token')

    TOKEN_REGEX: re.Pattern = re.compile(
        r'([a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]{27}|mfa\.[a-zA-Z0-9_\-]{84})'
    )

    def __init__(self, loop: AbstractEventLoop) -> None:
        self._loop: AbstractEventLoop = loop
        self._http: HTTPClient = None
        self._user: ClientUser = None

        self.__token: str = None

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop

    @property
    def http(self) -> HTTPClient:
        return self._http

    @property
    def api(self) -> Router:
        return self._http.api

    @property
    def user(self) -> ClientUser:
        return self._user

    @property
    def id(self) -> int:
        return None if self.user is None else self.user.id

    def put_token(self, token: str, /) -> None:
        # check here rather than throw a bad request,
        # this method should be called only once anyways
        if not self.TOKEN_REGEX.fullmatch(token):
            raise ValueError('invalid token given.')

        self.__token = token

    def establish_http(self, token: str = None, /, *, v: int = 9) -> None:
        if token is None and not self.__token:
            raise ValueError('token is required in order to log in.')

        if token is not None:
            self.put_token(token)

        self._http = HTTPClient(v=v, token=token)

    def patch_current_user(self, data: UserPayload, /) -> None:
        if self._user is None:
            self._user = ClientUser(self, data)
        else:
            self._user._load_data(data)

    async def update_user(self, /) -> None:
        data = await self.api.users.me.get()
        self.patch_current_user(data)
