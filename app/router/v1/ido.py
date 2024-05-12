import asyncio

from fastapi import APIRouter, Path, Query

from app.base import logger
from app.dependencies import CryptoDep, ProjectWhitelistCrudDep, LaunchpadProjectCrudDep
from app.env import settings
from app.schema import SignUserBalanceResponse, SignApprovedUserResponse
from app.services.ido import generate_balance_signature, generate_approved_user_signature
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
    for chain, balance in zip(str_chains, _balances):
        logger.info(f"Sign user balance chain: {chain}, balance: {balance}")

    balance = sum(balance for balance in _balances if isinstance(balance, int))

    signature = generate_balance_signature(
        user_address=user_address,
        balance=balance,
        chain_id=chain_id,
        launchpad_contract_address=contract_address,
        private_key=settings.ido_sign_account_private_key,
    )
    if not signature:
        return SignUserBalanceResponse(ok=False, error="Signature generation failed")
    return SignUserBalanceResponse(signature=signature)


@router.post("/{user_address}/sign-for-approved-user", response_model=SignApprovedUserResponse)
async def sign_approved_user(
    project_whitelist_crud: ProjectWhitelistCrudDep,
    launchpad_project_crud: LaunchpadProjectCrudDep,
    user_address: str = Path(
        pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"
    ),
    contract_address: str = Query(),
    contract_project_id: int = Query(),
    project_id: str = Query(),
) -> SignApprovedUserResponse:
    chain_id = (
        chains.blast_sepolia.id if settings.crypto_environment == "testnet" else chains.blast.id
    )

    if not (project := await launchpad_project_crud.find_by_id_or_slug(project_id)):
        return SignApprovedUserResponse(ok=False, error="Project not found")

    if project.whitelist_required and not (
        await project_whitelist_crud.user_is_in_whitelist(project.id, user_address)
    ):
        # check user in project whitelist
        return SignApprovedUserResponse(ok=False, error="User is not in project whitelist")

    # todo: check kyc

    signature = generate_approved_user_signature(
        user_address=user_address,
        contract_project_id=contract_project_id,
        chain_id=chain_id,
        launchpad_contract_address=contract_address,
        private_key=settings.ido_sign_account_private_key,
    )
    return SignApprovedUserResponse(signature=signature)
