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
optimism = ChainInfo(
    id=ChainId(10),
    name="Optimism",
)
bsc = ChainInfo(
    id=ChainId(56),
    name="Binance Smart Chain",
)
bsc_testnet = ChainInfo(
    id=ChainId(97),
    name="Binance Smart Chain Testnet",
    is_testnet=True,
)
polygon = ChainInfo(
    id=ChainId(137),
    name="Polygon",
)
polygon_mumbai = ChainInfo(
    id=ChainId(80001),
    name="Polygon Mumbai",
    is_testnet=True,
)
base = ChainInfo(
    id=ChainId(8453),
    name="Base",
)
arbitrum = ChainInfo(
    id=ChainId(42161),
    name="Arbitrum",
)
linea = ChainInfo(
    id=ChainId(59144),
    name="Linea",
)
linea_sepolia = ChainInfo(
    id=ChainId(59141),
    name="Linea Testnet",
    is_testnet=True,
)
blast = ChainInfo(
    id=ChainId(81457),
    name="Blast",
)
arbitrum_sepolia = ChainInfo(
    id=ChainId(421614),
    name="Arbitrum Testnet",
    is_testnet=True,
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
