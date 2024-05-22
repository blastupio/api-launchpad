from app.schema import ChainId
from app.services.coingecko.types import CoinGeckoPlatform
from app import chains


from_platform_to_chain_id = {
    CoinGeckoPlatform("ethereum"): ChainId(chains.ethereum.id),
    CoinGeckoPlatform("binance-smart-chain"): ChainId(chains.bsc.id),
    CoinGeckoPlatform("blast"): ChainId(chains.blast.id),
    CoinGeckoPlatform("polygon-pos"): ChainId(chains.polygon.id),
    CoinGeckoPlatform("base"): ChainId(chains.base.id),
    CoinGeckoPlatform("optimistic-ethereum"): ChainId(chains.optimism.id),
    CoinGeckoPlatform("arbitrum-one"): ChainId(chains.arbitrum.id),
    CoinGeckoPlatform("linea"): ChainId(chains.linea.id),
}

chain_id_to_native_coin_coingecko_id: dict[ChainId, str] = {
    ChainId(chains.ethereum.id): "ethereum",
    ChainId(chains.bsc.id): "binancecoin",
    ChainId(chains.polygon.id): "matic-network",
    ChainId(chains.blast.id): "ethereum",
    ChainId(chains.blast_sepolia.id): "ethereum",
    ChainId(chains.ethereum_sepolia.id): "ethereum",
    ChainId(chains.base_sepolia.id): "ethereum",
    ChainId(chains.base.id): "ethereum",
    ChainId(chains.optimism.id): "ethereum",
    ChainId(chains.linea.id): "ethereum",
    ChainId(chains.linea_sepolia.id): "ethereum",
    ChainId(chains.arbitrum.id): "ethereum",
    ChainId(chains.arbitrum_sepolia.id): "ethereum",
}

chain_id_to_testnet_coin_coingecko_id: dict[ChainId, dict[str, str]] = {
    ChainId(chains.blast_sepolia.id): {
        "0x3470769fba0aa949ecdaf83cad069fa2dc677389": "weth",
        "0x66ed1eeb6cef5d4ace858890704af9c339266276": "usdb",
    }
}
