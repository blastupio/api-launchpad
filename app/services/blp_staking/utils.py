from web3 import AsyncWeb3
from web3.contract import AsyncContract

from app.services.blp_staking.abi import STAKING_CONTRACT_ABI
from app.services.blp_staking.consts import BlpStakingPool


def get_pool_contract(web3: AsyncWeb3, pool: BlpStakingPool) -> AsyncContract:
    staking_contract = web3.eth.contract(
        address=pool.staking_contract_address,
        abi=STAKING_CONTRACT_ABI,
    )
    return staking_contract
