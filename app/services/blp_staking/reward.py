from web3 import Web3

from app.dependencies import get_launchpad_crypto
from app.services.blp_staking.consts import pool_by_id
from app.services.blp_staking.multicall import get_staked_balance_for_user_by_pool
from app.services.tiers import consts
from app.services.tiers.user_tier import get_user_tier


def _get_tier_coef(locked_balance_wei: int) -> float:
    user_tier = get_user_tier(locked_balance_wei)
    if user_tier is None or user_tier == consts.bronze_tier:
        return 1.0
    elif user_tier == consts.silver_tier:
        return 1.1
    elif user_tier == consts.gold_tier:
        return 1.2
    elif user_tier == consts.titanium_tier:
        return 1.5
    elif user_tier == consts.platinum_tier:
        return 1.7
    elif user_tier == consts.diamond_tier:
        return 2.0
    else:
        return 1.0


def calculate_bp_daily_reward(
    pool_locked_balance_wei: int, total_locked_blp: int, pool_id: int
) -> float:
    pool = pool_by_id[pool_id]
    locked_balance = float(Web3.from_wei(pool_locked_balance_wei, "ether"))
    tier_coef = _get_tier_coef(total_locked_blp)

    yearly_reward = locked_balance * (pool.apr_percent / 100) * pool.booster_points_coef * tier_coef
    daily_reward = round(yearly_reward / 360, 2)
    return daily_reward


async def get_blp_staking_daily_reward_for_user(user_address: str) -> float:
    crypto = get_launchpad_crypto()
    staked_blp = await crypto.get_blp_staking_value(user_address)

    staked_by_pool_id = await get_staked_balance_for_user_by_pool(
        user_address,
        {pool_id: pool.staking_contract_address for pool_id, pool in pool_by_id.items()},
    )
    reward: float = 0.0
    for pool_id, staked_balance in staked_by_pool_id.items():
        points_amount = calculate_bp_daily_reward(
            staked_balance,
            staked_blp,
            pool_id,
        )
        reward += points_amount
    return reward
