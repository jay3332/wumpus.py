from typing import Any, Awaitable, Callable, Dict, Literal, Tuple, Union


__all__: Tuple[str, ...] = (
    'JSON',
    'Snowflake',
    'HTTPVersion',
    'GatewayVersion',
    'HTTPRequestMethod'
)


# Common
JSON = Dict[str, Any]  # This may be changed in the future
Snowflake = int  # Type alias for readability

EmitterCallback = Callable[[Any, ...], Union[Awaitable[Any], Any]]

HTTPVersion = Literal[3, 4, 5, 6, 7, 8, 9]
GatewayVersion = Literal[4, 5, 6, 7, 8, 9]

HTTPRequestMethod = Literal['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
