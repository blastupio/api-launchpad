import asyncio

from app import chains
from app.base import logger
from app.env import settings
from app.services.ido_staking.consts import (
    WETH_TESTNET_ADDRESS,
    USDB_TESTNET_ADDRESS,
    WETH_ADDRESS,
    USDB_ADDRESS,
)
from app.services.ido_staking.multicall import get_locked_amount_for_user
from app.services.prices import get_tokens_price_for_chain


async def get_user_usd_tvl(user_address: str) -> float | None:
    native_token_address = WETH_TESTNET_ADDRESS if settings.app_env == "dev" else WETH_ADDRESS
    stablecoin_token_address = USDB_TESTNET_ADDRESS if settings.app_env == "dev" else USDB_ADDRESS

    chain_id = chains.blast_sepolia.id if settings.app_env == "dev" else chains.blast.id
    token_addresses = [native_token_address, stablecoin_token_address]
    user_locked_amount, price_for_tokens = await asyncio.gather(
        get_locked_amount_for_user(user_address, native_token_address, stablecoin_token_address),
        get_tokens_price_for_chain(chain_id, token_addresses),
        return_exceptions=True,
    )
    if isinstance(user_locked_amount, Exception):
        logger.error(f"user tvl[{user_address}]: can't get locked amount: {user_locked_amount=}")
        return None
    if not price_for_tokens:
        logger.error(f"user tvl[{user_address}]: no price for staked tokens: {token_addresses=}")
        return None
    elif len(price_for_tokens) < 2:
        # 2 is number of tokens (native and stablecoin)
        logger.error(
            f"user tvl[{user_address}]: no price for some of staked tokens: {price_for_tokens=}"
        )
        return None
    elif isinstance(price_for_tokens, Exception):
        logger.error(
            f"user tvl[{user_address}]: can't get price for staked tokens: {price_for_tokens=}"
        )
        return None

    native_usd_tvl = user_locked_amount.native * price_for_tokens[native_token_address.lower()]
    stablecoin_usd_tvl = (
        user_locked_amount.stablecoin * price_for_tokens[stablecoin_token_address.lower()]
    )
    total_usd_tvl = round(native_usd_tvl + stablecoin_usd_tvl, 2)
    return total_usd_tvl
