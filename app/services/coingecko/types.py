from typing import TypedDict


class ListCoin(TypedDict):
    id: str  # noqa
    symbol: str
    name: str
    platforms: dict[str, str]  # key: platform name, value: token address on that platform
