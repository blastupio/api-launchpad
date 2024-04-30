import asyncio

from fastapi import APIRouter, Path, Query

from app.dependencies import CryptoDep
from app.env import settings
from app.schema import SignUserBalanceResponse
from app.services.ido import generate_signature
from app import chains


router = APIRouter(prefix="/ido", tags=["ido"])


@router.post("/{user_address}/sign-balance", response_model=SignUserBalanceResponse)
async def sign_user_balance(
    crypto: CryptoDep,
    user_address: str = Path(
        pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"
    ),
    contract_address: str = Query(),
) -> SignUserBalanceResponse:
    str_chains = ("eth", "polygon", "bsc", "blast")
    chain_id = chains.blast.id if crypto.environment == "mainnet" else chains.blast_sepolia.id

    _balances = await asyncio.gather(
        *[crypto.get_blastup_token_balance(chain, user_address) for chain in str_chains]
    )
    balance = sum(balance for balance in _balances if isinstance(balance, int))

    signature = generate_signature(
        user_address=user_address,
        balance=balance,
        chain_id=chain_id,
        launchpad_contract_address=contract_address,
        private_key=settings.ido_sign_account_private_key,
    )
    return {"signature": signature}
