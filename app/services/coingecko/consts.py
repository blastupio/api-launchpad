from app.schema import ChainId

from_platform_to_chain_id = {
    "ethereum": ChainId(1),
    "binance-smart-chain": ChainId(56),
    "blast": ChainId(81457),
    "polygon-pos": ChainId(137),
}

chain_id_to_native_coin_coingecko_id: dict[int, str] = {
    1: "ethereum",
    56: "binancecoin",
    137: "matic-network",
    81457: "blast-old",
}
