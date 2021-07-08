from typing import Literal



from typing import Any, Dict, Literal, Tuple


__all__: Tuple[str, ...] = (
    'JSON',
    'HTTPVersion',
    'GatewayVersion',
    'HTTPRequestMethod'
)


JSON = Dict[str, Any]  # This may be changed in the future

HTTPVersion = Literal[3, 4, 5, 6, 7, 8, 9]
GatewayVersion = Literal[4, 5, 6, 7, 8, 9]

HTTPRequestMethod = Literal['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
