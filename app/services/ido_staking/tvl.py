import math

from app import chains
from app.base import logger
from app.env import settings
from app.schema import UserTvlIdoFarming, TotalTvlIdoFarming
from app.services.ido_staking.cache import tvl_cache, user_tvl_cache

from app.services.ido_staking.multicall import get_locked_amount_for_user, get_locked_amount
from app.services.prices import get_tokens_price_for_chain


async def get_user_usd_tvl(user_address: str) -> UserTvlIdoFarming | None:
    chain_id = chains.blast_sepolia.id if settings.app_env == "dev" else chains.blast.id
    native_token_address = settings.blast_weth_address
    stablecoin_token_address = settings.blast_usdb_address
    token_addresses = [native_token_address, stablecoin_token_address]

    locked_amount = await user_tvl_cache.get_locked_amount(user_address)
    if locked_amount is None:
        try:
            locked_amount = await get_locked_amount_for_user(
                user_address, native_token_address, stablecoin_token_address
            )
            await user_tvl_cache.set_locked_amount(user_address, locked_amount)
        except Exception as e:
            logger.error(f"user tvl[{user_address}]: can't get locked amount: {e}")
            return None

    if isinstance(locked_amount, Exception):
        logger.error(f"user tvl[{user_address}]: can't get locked amount: {locked_amount=}")
        return None
    if not (price_for_tokens := await get_tokens_price_for_chain(chain_id, token_addresses)):
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

    native_usd_tvl = round(locked_amount.native * price_for_tokens[native_token_address.lower()], 4)
    stablecoin_usd_tvl = round(
        locked_amount.stablecoin * price_for_tokens[stablecoin_token_address.lower()], 4
    )
    total_usd_tvl = round(native_usd_tvl + stablecoin_usd_tvl, 2)
    return UserTvlIdoFarming(
        native=native_usd_tvl, stablecoin=stablecoin_usd_tvl, total=total_usd_tvl
    )


async def get_total_usd_tvl() -> TotalTvlIdoFarming | None:
    chain_id = chains.blast_sepolia.id if settings.app_env == "dev" else chains.blast.id

    native_token_address = settings.blast_weth_address
    stablecoin_token_address = settings.blast_usdb_address
    token_addresses = [native_token_address, stablecoin_token_address]

    locked_amount = await tvl_cache.get_locked_amount()
    if locked_amount is None:
        try:
            locked_amount = await get_locked_amount(native_token_address, stablecoin_token_address)
            await tvl_cache.set_locked_amount(locked_amount)
        except Exception as e:
            logger.error(f"total tvl: can't get locked amount: {e}")
            return None

    if not (price_for_tokens := await get_tokens_price_for_chain(chain_id, token_addresses)):
        logger.error(f"total tvl: no price for staked tokens: {token_addresses=}")
        return None
    elif len(price_for_tokens) < 2:
        # 2 is number of tokens (native and stablecoin)
        logger.error(f"total tvl: no price for some of staked tokens: {price_for_tokens=}")
        return None
    elif isinstance(price_for_tokens, Exception):
        logger.error(f"total tvl: can't get price for staked tokens: {price_for_tokens=}")
        return None

    native_usd_tvl = round(locked_amount.native * price_for_tokens[native_token_address.lower()], 4)
    stablecoin_usd_tvl = round(
        locked_amount.stablecoin * price_for_tokens[stablecoin_token_address.lower()], 4
    )
    total_usd_tvl = round(native_usd_tvl + stablecoin_usd_tvl, 2)
    return TotalTvlIdoFarming(
        native=native_usd_tvl, stablecoin=stablecoin_usd_tvl, total=total_usd_tvl
    )


def get_ido_staking_daily_reward(total_usd_staked: float) -> int | None:
    if total_usd_staked < 100:
        return None
    points_amount = math.ceil(total_usd_staked / 100)
    return points_amount


async def get_ido_staking_daily_reward_for_user(user_address: str) -> int:
    user_tvl = await get_user_usd_tvl(user_address)
    points = get_ido_staking_daily_reward(user_tvl.total) if user_tvl is not None else 0
    return points
