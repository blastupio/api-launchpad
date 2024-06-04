from eth_utils import encode_hex, function_abi_to_4byte_selector
from web3._utils.abi import get_abi_output_types

from app.abi import LAUNCHPAD_PLACE_TOKENS_ABI, TRY_AGGREGATE_ABI, LAUNCHPAD_USERS_ABI
from app.services.ido_staking.abi import STAKING_USER_INFO_ABI, STAKING_TOTAL_SUPPLY_ABI


def encode_hex_fn_abi(fn_abi):
    return encode_hex(function_abi_to_4byte_selector(fn_abi))


placed_tokens_selector = encode_hex_fn_abi(LAUNCHPAD_PLACE_TOKENS_ABI)
users_selector = encode_hex_fn_abi(LAUNCHPAD_USERS_ABI)
staking_user_info_selector = encode_hex_fn_abi(STAKING_USER_INFO_ABI)
staking_total_supply_selector = encode_hex_fn_abi(STAKING_TOTAL_SUPPLY_ABI)
try_aggregate_selector = encode_hex_fn_abi(TRY_AGGREGATE_ABI)
try_aggregate_output_types = get_abi_output_types(TRY_AGGREGATE_ABI)
