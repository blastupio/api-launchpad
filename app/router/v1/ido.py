import asyncio

from fastapi import APIRouter, Path

from app.dependencies import CryptoDep
from app.env import IDO_SIGN_ACCOUNT_PRIVATE_KEY, LAUNCHPAD_CONTRACT_ADDRESS
from app.schema import SignUserBalanceResponse
from app.services.ido import generate_signature



router = APIRouter(prefix="/ido", tags=["ido"])


@router.post("/{user_address}/sign-balance", response_model=SignUserBalanceResponse)
async def sign_user_balance(
    crypto: CryptoDep,
    user_address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"),
) -> SignUserBalanceResponse:
    chains = ("eth", "polygon", "bsc", "blast")
    chain_id = 81457 if crypto.environment == "mainnet" else 168587773

    _balances = await asyncio.gather(*[crypto.get_token_balance(chain, user_address) for chain in chains])
    balance = sum(balance for balance in _balances if isinstance(balance, int))

    signature = generate_signature(
        user_address=user_address,
        balance=balance,
        chain_id=chain_id,
        launcpad_contract_address=LAUNCHPAD_CONTRACT_ADDRESS,
        private_key=IDO_SIGN_ACCOUNT_PRIVATE_KEY,
    )
    return {"signature": signature}
