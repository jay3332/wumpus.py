from typing import Any, Dict, NamedTuple, Literal, Tuple, Type
from .connection import Connection


FormatTypes = Literal['png', 'jpg', 'jpeg', 'webp', 'gif']
StaticFormatTypes = Literal['png', 'jpg', 'jpeg', 'webp']
AssetSizes = Literal[16, 32, 64, 128, 256, 512, 1024, 2048, 4096]


__all__ = (
    'AssetMeta',
    'BaseAsset',
    'AssetInfo',
    'Asset'
)


class AssetMeta(type):
    def __new__(
        mcs: Type[type],
        name: str,
        base: Tuple[type, ...],
        attrs: Dict[str, Any],
        /,
        *,
        cdn_url: str = 'https://cdn.discordapp.com/'
    ) -> type:
        attrs['__cdn_url__'] = cdn_url
        return super().__new__(mcs, name, base, attrs)


class BaseAsset(metaclass=AssetMeta):
    __cdn_url__: str


class AssetInfo(NamedTuple):
    format: FormatTypes = None
    static_format: StaticFormatTypes = None
    size: AssetSizes = None


BlankAssetInfo = AssetInfo()


class Asset(BaseAsset):
    # TODO: easier way to modify :class:`AssetInfo`

    __slots__ = ('_connection', '_params', '_animated', '_url', '_hash')

    def __init__(
        self,
        connection: Connection,
        /,
        *,
        url: str,
        info: AssetInfo = BlankAssetInfo,
        animated: bool = False,
        hash: str = None
    ):
        self._connection: Connection = connection
        self._animated: bool = animated
        self._info: AssetInfo = info
        self._hash: str = hash
        self._url: str = url

    @property
    def base_url(self, /) -> str:
        return self.__cdn_url__ + self._url

    @property
    def url(self, /) -> str:
        if not len(self._params):
            return self.base_url

        url = self.base_url + '.' + self.format

        if self.size:
            url += f'?size={self.size}'
        return url

    @property
    def animated(self, /) -> str:
        return self._animated

    @property
    def hash(self, /) -> str:
        return self._hash

    @property
    def default_format(self, /) -> FormatTypes:
        return 'gif' if self._animated else 'png'

    @property
    def format(self, /) -> FormatTypes:
        return self._info.format or self.default_format

    @property
    def size(self, /) -> AssetSizes:
        return self._info.size

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f'<Asset hash={self.hash!r} format={self._info.format!r} size={self._info.size!r}>'
