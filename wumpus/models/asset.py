from typing import Any, Dict, NamedTuple, Literal, Tuple, Type, TypeVar, overload
from ..core.connection import Connection


T = TypeVar('T', bound='Asset')

FormatTypes = Literal['png', 'jpg', 'jpeg', 'webp', 'gif']
StaticFormatTypes = Literal['png', 'jpg', 'jpeg', 'webp']
AssetSizes = Literal[16, 32, 64, 128, 256, 512, 1024, 2048, 4096]

VALID_FORMAT_TYPES = 'png', 'jpg', 'jpeg', 'webp', 'gif'
VALID_STATIC_FORMAT_TYPES = 'png', 'jpg', 'jpeg', 'webp'
VALID_ASSET_SIZES = 16, 32, 64, 128, 256, 512, 1024, 2048, 4096

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


def _make_asset_info(
    format: FormatTypes = None,
    static_format: StaticFormatTypes = None,
    size: AssetSizes = None,
    /
) -> AssetInfo:
    if format is not None and format not in VALID_FORMAT_TYPES:
        raise ValueError(f'invalid asset format {format!r}.')

    if static_format is not None and static_format not in VALID_STATIC_FORMAT_TYPES:
        raise ValueError(f'invalid static asset format {format!r}.')

    if size is not None and size not in VALID_ASSET_SIZES:
        raise ValueError('asset size must be a power of two between 16 and 4096')

    return AssetInfo(format, static_format, size)


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
        if not len(self._info):
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
    def static_format(self, /) -> StaticFormatTypes:
        return self._info.static_format or 'png'

    @property
    def default_format(self, /) -> FormatTypes:
        return 'gif' if self._animated else self.static_format

    @property
    def format(self, /) -> FormatTypes:
        return self._info.format or self.default_format

    @property
    def size(self, /) -> AssetSizes:
        return self._info.size

    def _copy(self: T, info: AssetInfo, /) -> T:
        return self.__class__(
            self._connection,
            animated=self.animated,
            url=self._url,
            info=info,
            hash=self.hash
        )

    def with_format(self: T, format: FormatTypes, /) -> T:
        new_info = _make_asset_info(format, self._info.size, self._info.static_format)
        return self._copy(new_info)

    def with_size(self: T, size: AssetSizes, /) -> T:
        new_info = _make_asset_info(self._info.format, size, self._info.static_format)
        return self._copy(new_info)

    def with_static_format(self: T, static_format: StaticFormatTypes, /) -> T:
        new_info = _make_asset_info(self._info.format, self._info.size, static_format)
        return self._copy(new_info)

    def replace(
        self: T,
        /,
        *,
        format: FormatTypes = None,
        size: AssetSizes = None,
        static_format: StaticFormatTypes = None
    ) -> T:
        new_info = _make_asset_info(
            format or self._info.format,
            size or self._info.size,
            static_format or self._info.static_format
        )
        return self._copy(new_info)

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f'<Asset hash={self.hash!r} format={self._info.format!r} size={self._info.size!r}>'

    def __copy__(self: T) -> T:
        return self._copy(self._info)

    def __format__(self, format: str) -> str:
        if not format:
            return self.url

        return str(self.with_format(format))

    @overload
    def __call__(
        self: T,
        /,
        *,
        format: FormatTypes = None,
        size: AssetSizes = None,
        static_format: StaticFormatTypes = None
    ) -> T:
        ...

    def __call__(self: T, /, **kwargs) -> T:
        return self.replace(**kwargs)
