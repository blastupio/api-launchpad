import math

from web3 import AsyncWeb3, Web3
from web3.contract import AsyncContract

from app.services.blp_staking.abi import STAKING_CONTRACT_ABI
from app.services.blp_staking.consts import BlpStakingPool, pool_by_id
from app.services.tiers import consts
from app.services.tiers.user_tier import get_user_tier


def get_pool_contract(web3: AsyncWeb3, pool: BlpStakingPool) -> AsyncContract:
    staking_contract = web3.eth.contract(
        address=pool.staking_contract_address,
        abi=STAKING_CONTRACT_ABI,
    )
    return staking_contract


def get_tier_coef(locked_balance_wei: int) -> float:
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


def calculate_bp_daily_reward(locked_balance_wei: int, total_locked_blp: int, pool_id: int) -> int:
    pool = pool_by_id[pool_id]
    locked_balance = float(Web3.from_wei(locked_balance_wei, "ether"))
    tier_coef = get_tier_coef(total_locked_blp)

    reward_for_period = (
        locked_balance * (pool.apr_percent / 100) * pool.booster_points_coef * tier_coef
    )
    daily_reward = math.ceil(reward_for_period / pool.lock_up_days)
    return daily_reward
