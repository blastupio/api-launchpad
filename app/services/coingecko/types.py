from typing import TypedDict, NewType


CoinGeckoPlatform = NewType("CoinGeckoPlatform", str)

CoinGeckoCoinId = NewType("CoinGeckoCoinId", str)


class ListCoin(TypedDict):
    id: str  # noqa
    symbol: str
    name: str
    platforms: dict[
        CoinGeckoPlatform, str
    ]  # key: platform name, value: token address on that platform
