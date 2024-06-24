from eth_utils import add_0x_prefix
from web3._utils.contracts import encode_abi

from app.abi import TRY_AGGREGATE_ABI
from app.consts import MULTICALL_ADDRESS
from app.selectors import (
    blp_staking_users_selector,
    try_aggregate_selector,
    try_aggregate_output_types,
)
from app.services.blp_staking.abi import BLP_STAKING_USERS_ABI
from app.services.web3_nodes import web3_node
from eth_abi import decode

from app.types import BlpStakingUser

USERS_TYPES = [x["type"] for x in BLP_STAKING_USERS_ABI["outputs"]]


async def get_staked_balance(contract_address: str, user_addresses: list[str]) -> dict[str, int]:
    web3 = await web3_node.get_web3("blast")
    encoded = (
        (
            contract_address,
            encode_abi(
                web3,
                BLP_STAKING_USERS_ABI,
                arguments=[web3.to_checksum_address(user_address)],
                data=blp_staking_users_selector,
            ),
        )
        for user_address in user_addresses
    )
    data = add_0x_prefix(
        encode_abi(
            web3,
            TRY_AGGREGATE_ABI,
            (False, [(launchpad_addr, enc) for launchpad_addr, enc in encoded]),
            try_aggregate_selector,
        )
    )
    tx_raw_data = await web3.eth.call({"to": MULTICALL_ADDRESS, "data": data})
    output_data = web3.codec.decode(try_aggregate_output_types, tx_raw_data)[0]
    res = {}
    for (success, data), user_address in zip(output_data, user_addresses):
        if not data or not success:
            continue
        info = BlpStakingUser(
            *decode(
                types=USERS_TYPES,
                data=data,
            )
        )
        res[user_address.lower()] = info.balance
    return res


async def get_staked_balance_for_user_by_pool(
    user_address: str, contract_addresses_by_pool_id: dict[int, str]
) -> dict[int, int]:
    web3 = await web3_node.get_web3("blast")
    encoded = (
        (
            web3.to_checksum_address(contract_address),
            encode_abi(
                web3,
                BLP_STAKING_USERS_ABI,
                arguments=[web3.to_checksum_address(user_address)],
                data=blp_staking_users_selector,
            ),
        )
        for contract_address in contract_addresses_by_pool_id.values()
    )
    data = add_0x_prefix(
        encode_abi(
            web3,
            TRY_AGGREGATE_ABI,
            (False, [(addr, enc) for addr, enc in encoded]),
            try_aggregate_selector,
        )
    )
    tx_raw_data = await web3.eth.call({"to": MULTICALL_ADDRESS, "data": data})
    output_data = web3.codec.decode(try_aggregate_output_types, tx_raw_data)[0]
    staked_by_pool_id = {}
    for (success, data), pool_id in zip(output_data, contract_addresses_by_pool_id.keys()):
        if not data or not success:
            continue
        info = BlpStakingUser(
            *decode(
                types=USERS_TYPES,
                data=data,
            )
        )
        staked_by_pool_id[pool_id] = info.balance
    return staked_by_pool_id
