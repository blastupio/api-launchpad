from app.schema import ChainId
from app.services.coingecko.types import CoinGeckoPlatform


from_platform_to_chain_id = {
    CoinGeckoPlatform("ethereum"): ChainId(1),
    CoinGeckoPlatform("binance-smart-chain"): ChainId(56),
    CoinGeckoPlatform("blast"): ChainId(81457),
    CoinGeckoPlatform("polygon-pos"): ChainId(137),
}

chain_id_to_native_coin_coingecko_id: dict[int, str] = {
    1: "ethereum",
    56: "binancecoin",
    137: "matic-network",
    81457: "blast-old",
}
