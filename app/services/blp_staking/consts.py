from dataclasses import dataclass

from eth_typing import ChecksumAddress
from web3 import Web3, AsyncWeb3
from web3.contract import AsyncContract

from app.env import settings
from app.services.blp_staking.abi import STAKING_CONTRACT_ABI


@dataclass(frozen=True)
class BlpStakingPool:
    id: int  # noqa
    lock_up_days: int
    apr_percent: int
    booster_points_coef: float
    staking_contract_address: ChecksumAddress


pool_1 = BlpStakingPool(
    id=1,
    lock_up_days=90,
    apr_percent=12,
    booster_points_coef=1,
    staking_contract_address=Web3.to_checksum_address(settings.staking_blp_contract_pool_1),
)
pool_2 = BlpStakingPool(
    id=2,
    lock_up_days=180,
    apr_percent=18,
    booster_points_coef=1.5,
    staking_contract_address=Web3.to_checksum_address(settings.staking_blp_contract_pool_2),
)
pool_3 = BlpStakingPool(
    id=3,
    lock_up_days=360,
    apr_percent=24,
    booster_points_coef=2,
    staking_contract_address=Web3.to_checksum_address(settings.staking_blp_contract_pool_3),
)

pool_by_id: dict[int, BlpStakingPool] = {pool.id: pool for pool in (pool_1, pool_2, pool_3)}


def get_blp_staking_contract(web3: AsyncWeb3, pool: BlpStakingPool) -> AsyncContract:
    def get_pool_contract(contract_address: str) -> AsyncContract:
        staking_contract = web3.eth.contract(
            address=contract_address,
            abi=STAKING_CONTRACT_ABI,
        )
        return staking_contract

    contract_by_pool = {
        pool_1: get_pool_contract(pool_1.staking_contract_address),
        pool_2: get_pool_contract(pool_2.staking_contract_address),
        pool_3: get_pool_contract(pool_3.staking_contract_address),
    }
    return contract_by_pool[pool]
