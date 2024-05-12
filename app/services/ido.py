from web3 import Web3
from eth_account.messages import encode_defunct, SignableMessage
from eth_account import Account

from app.base import logger


def sign_message(message: SignableMessage, private_key: str) -> str | None:
    """
    Returns the signature of the message signed with the private key.
    """
    if not private_key:
        logger.error("No private key provided for signing message")
        return

    acc = Account.from_key(private_key)
    signature = acc.sign_message(message).signature.hex()
    return signature


def generate_balance_signature(
    user_address: str,
    balance: int,
    chain_id: int,
    launchpad_contract_address: str,
    private_key: str,
) -> str:
    user_address = Web3.to_checksum_address(user_address)
    launchpad_contract_address = Web3.to_checksum_address(launchpad_contract_address)
    balance = Web3.to_wei(balance, unit="ether")

    logger.info(
        f"Sign user balance: {user_address=} {balance=} {launchpad_contract_address=} {chain_id=}"
    )
    payload = Web3.solidity_keccak(
        ["address", "uint256", "address", "uint256"],
        [user_address, balance, launchpad_contract_address, chain_id],
    )
    msg = encode_defunct(payload)
    return sign_message(msg, private_key)


def generate_approved_user_signature(
    user_address: str,
    contract_project_id: int,
    chain_id: int,
    launchpad_contract_address: str,
    private_key: str,
) -> str:
    user_address = Web3.to_checksum_address(user_address)
    launchpad_contract_address = Web3.to_checksum_address(launchpad_contract_address)

    payload = Web3.solidity_keccak(
        ["address", "uint256", "address", "uint256"],
        [user_address, contract_project_id, launchpad_contract_address, chain_id],
    )
    msg = encode_defunct(payload)
    return sign_message(msg, private_key)
