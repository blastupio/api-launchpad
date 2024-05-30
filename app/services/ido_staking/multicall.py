from collections import defaultdict

from eth_utils import add_0x_prefix
from web3._utils.contracts import encode_abi
from eth_abi import decode

from app.abi import TRY_AGGREGATE_ABI
from app.services.ido_staking.abi import STAKING_USER_INFO_ABI
from app.consts import MULTICALL_ADDRESS
from app.env import settings
from app.selectors import (
    try_aggregate_selector,
    try_aggregate_output_types,
    staking_user_info_selector,
)
from app.services.web3_nodes import web3_node
from app.types import StakingUserInfo


async def get_locked_balance(
    token_address: str,
    user_addresses: list[str],
) -> dict[str, dict[str, int]]:
    web3 = await web3_node.get_web3("blast")
    yield_staking_addr = web3.to_checksum_address(settings.yield_staking_contract_addr)
    token_address = web3.to_checksum_address(token_address)
    encoded = (
        (
            yield_staking_addr,
            encode_abi(
                web3,
                STAKING_USER_INFO_ABI,
                arguments=[token_address, web3.to_checksum_address(user_address)],
                data=staking_user_info_selector,
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
    res = defaultdict(dict)
    for (success, data), user_address in zip(output_data, user_addresses):
        if not data or not success:
            continue
        info = StakingUserInfo(
            *decode(
                types=[x["type"] for x in STAKING_USER_INFO_ABI["outputs"][0]["components"]],
                data=data,
            )
        )
        res[token_address.lower()][user_address.lower()] = info.locked_balance
    return res
