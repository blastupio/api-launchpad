from app.schema import ChainId
from app.services.coingecko.types import CoinGeckoPlatform
from app import chains


from_platform_to_chain_id = {
    CoinGeckoPlatform("ethereum"): ChainId(chains.ethereum.id),
    CoinGeckoPlatform("binance-smart-chain"): ChainId(chains.bsc.id),
    CoinGeckoPlatform("blast"): ChainId(chains.blast.id),
    CoinGeckoPlatform("polygon-pos"): ChainId(chains.polygon.id),
}

chain_id_to_native_coin_coingecko_id: dict[ChainId, str] = {
    ChainId(chains.ethereum.id): "ethereum",
    ChainId(chains.bsc.id): "binancecoin",
    ChainId(chains.polygon.id): "matic-network",
    ChainId(chains.blast.id): "ethereum",
    ChainId(chains.blast_sepolia.id): "ethereum",
    ChainId(chains.ethereum_sepolia.id): "ethereum",
}

chain_id_to_testnet_coin_coingecko_id: dict[ChainId, dict[str, str]] = {
    ChainId(chains.blast_sepolia.id): {
        "0x4200000000000000000000000000000000000022": "usdb",
        "0x4200000000000000000000000000000000000023": "weth",
    }
}
