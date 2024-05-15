from typing import Any

from eth_utils import add_0x_prefix
from web3 import AsyncWeb3, Web3
from web3._utils.contracts import encode_abi

from app.abi import LAUNCHPAD_PLACE_TOKENS_ABI, TRY_AGGREGATE_ABI
from app.consts import MULTICALL_ADDRESS
from app.env import settings
from app.selectors import placed_tokens_selector, try_aggregate_selector, try_aggregate_output_types


async def get_multicall_token_placed(
    web3: AsyncWeb3, contract_project_id_by_project_id: dict[str, int]
) -> tuple[Any, ...]:
    # call tokenPlaced function for multiple contract_project_id at once
    launchpad_address = Web3.to_checksum_address(settings.launchpad_contract_address)
    encoded = (
        (
            launchpad_address,
            encode_abi(
                web3,
                LAUNCHPAD_PLACE_TOKENS_ABI,
                arguments=[contract_project_id],
                data=placed_tokens_selector,
            ),
        )
        for contract_project_id in contract_project_id_by_project_id.values()
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
    return output_data
