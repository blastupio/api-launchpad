from web3 import Web3
from eth_account.messages import encode_defunct
from eth_account import Account


def generate_signature(user_address: str, balance: int, chain_id: int, launcpad_contract_address: str, private_key: str) -> str:
    user_address = Web3.to_checksum_address(user_address) if not Web3.is_checksum_address(user_address) else user_address

    payload = Web3.solidity_keccak(
        ["address", "uint256", "address", "uint256"],
        [user_address, balance, launcpad_contract_address, chain_id],
    )
    msg = encode_defunct(payload)
    acc = Account.from_key(private_key)
    signature = acc.sign_message(msg).signature.hex()
    return signature
