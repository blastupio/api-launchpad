from app.consts import NATIVE_TOKEN_ADDRESS
from app.schema import ChainId, Address
from app.services.coingecko.client import (
    get_coingecko_id_by_chain_id_and_address,
    get_token_address_by_coingecko_id,
    get_coingecko_price,
)
from app.services.coingecko.consts import chain_id_to_native_coin_coingecko_id


async def get_tokens_price(chain_id: ChainId, token_addresses: list[str]) -> dict[Address, float]:
    if not token_addresses:
        return {}
    coingecko_id_by_chain_id_and_address = await get_coingecko_id_by_chain_id_and_address()
    token_address_by_coingecko_id = get_token_address_by_coingecko_id(
        chain_id, coingecko_id_by_chain_id_and_address
    )

    token_ids_with_nans = (
        coingecko_id_by_chain_id_and_address.get(chain_id, {}).get(token_address.lower())
        for token_address in token_addresses
    )
    token_ids = [token_id for token_id in token_ids_with_nans if token_id]
    if NATIVE_TOKEN_ADDRESS in token_addresses and chain_id in chain_id_to_native_coin_coingecko_id:
        native_coin_id = chain_id_to_native_coin_coingecko_id[chain_id]
        token_ids.append(native_coin_id)
        token_address_by_coingecko_id[native_coin_id] = NATIVE_TOKEN_ADDRESS

    if not token_ids:
        return {}

    coingecko_prices: dict[str, dict[str, float]] = await get_coingecko_price(token_ids)
    res: dict[Address, float] = {}
    for coingecko_id, coingecko_price in coingecko_prices.items():
        token_address = token_address_by_coingecko_id.get(coingecko_id)
        if token_address and (usd_price := coingecko_price.get("usd")):
            res[Address(token_address)] = usd_price
    return res
