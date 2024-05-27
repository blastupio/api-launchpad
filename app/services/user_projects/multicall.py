from eth_utils import add_0x_prefix
from web3._utils.contracts import encode_abi
from eth_abi import decode

from app.abi import LAUNCHPAD_USERS_ABI, TRY_AGGREGATE_ABI
from app.consts import MULTICALL_ADDRESS
from app.env import settings
from app.selectors import users_selector, try_aggregate_selector, try_aggregate_output_types
from app.services.web3_nodes import web3_node
from app.types import UserInfo


async def get_projects_ids_of_user(user_address: str, contract_project_ids: list[int]) -> list[int]:
    # call userInfo function for multiple contract_project_id at once
    web3 = await web3_node.get_web3("blast")
    launchpad_address = web3.to_checksum_address(settings.launchpad_contract_address)
    user_address = web3.to_checksum_address(user_address)
    encoded = (
        (
            launchpad_address,
            encode_abi(
                web3,
                LAUNCHPAD_USERS_ABI,
                arguments=[contract_project_id, user_address],
                data=users_selector,
            ),
        )
        for contract_project_id in contract_project_ids
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
    project_ids_of_user = []
    for (success, data), contract_project_id in zip(output_data, contract_project_ids):
        if not data or not success:
            continue
        info = UserInfo(
            *decode(types=[x["type"] for x in LAUNCHPAD_USERS_ABI["outputs"]], data=data)
        )
        if info.registered:
            project_ids_of_user.append(contract_project_id)
    return project_ids_of_user
