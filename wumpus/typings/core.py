from typing import Any, Awaitable, Dict, Literal, Protocol, Tuple, Union


__all__: Tuple[str, ...] = (
    'JSON',
    'Snowflake',
    'HTTPVersion',
    'GatewayVersion',
    'ValidDeleteMessageDays'
    'HTTPRequestMethod',
    'TimestampStyle',
    'EmitterCallback'
)


# Common
JSON = Dict[str, Any]  # This may be changed in the future
Snowflake = int  # Type alias for readability

HTTPVersion = Literal[3, 4, 5, 6, 7, 8, 9]
GatewayVersion = Literal[4, 5, 6, 7, 8, 9]
ValidDeleteMessageDays = Literal[0, 1, 2, 3, 4, 5, 6, 7]

HTTPRequestMethod = Literal['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

TimestampStyle = Literal['f', 'F', 'd', 'D', 't', 'T', 'R']


class EmitterCallback(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Union[Awaitable[Any], Any]:
        ...
