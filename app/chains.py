from dataclasses import dataclass

from app.schema import ChainId


@dataclass(frozen=True)
class ChainInfo:
    id: ChainId  # noqa
    name: str
    is_testnet: bool = False


ethereum = ChainInfo(
    id=ChainId(1),
    name="Ethereum",
)
bsc = ChainInfo(
    id=ChainId(56),
    name="Binance Smart Chain",
)
polygon = ChainInfo(
    id=ChainId(137),
    name="Polygon",
)
blast = ChainInfo(
    id=ChainId(81457),
    name="Blast",
)
