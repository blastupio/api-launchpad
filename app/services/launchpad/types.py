from typing import NamedTuple, TypedDict


class LaunchpadTransaction(NamedTuple):
    user_address: str
    txn_hash: str
    contract_project_id: int
    token_amount: int
    chain_id: int


class BuyTokensInput(TypedDict):
    id: int  # noqa
    paymentContract: str
    volume: int
    receiver: str
    signature: str
