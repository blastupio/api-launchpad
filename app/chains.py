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
base = ChainInfo(
    id=ChainId(8453),
    name="Base",
)
blast = ChainInfo(
    id=ChainId(81457),
    name="Blast",
)
blast_sepolia = ChainInfo(
    id=ChainId(168587773),
    name="Blast Testnet",
    is_testnet=True,
)
ethereum_sepolia = ChainInfo(
    id=ChainId(11155111),
    name="Ethereum Testnet",
    is_testnet=True,
)
base_sepolia = ChainInfo(
    id=ChainId(84532),
    name="Base Testnet",
    is_testnet=True,
)
