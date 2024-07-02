from functools import partial

from fastapi import APIRouter, Body
from web3.exceptions import TransactionNotFound, TimeExhausted

from app.base import logger
from app.dependencies import CryptoDep, LaunchpadProjectCrudDep, TransactionsCrudDep, RedisDep
from app.env import settings
from app.models import ProjectType
from app.schema import StoreTransactionRequest, StoreTransactionResponse
from app.services.launchpad.utils import get_crypto_contracts
from app.tasks import (
    monitor_and_save_launchpad_events,
    monitor_and_save_multichain_launchpad_events,
)
from app.utils import get_data_with_cache

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("")
async def store_transaction(
    transactions_crud: TransactionsCrudDep,
    projects_crud: LaunchpadProjectCrudDep,
    crypto: CryptoDep,
    redis: RedisDep,
    payload: StoreTransactionRequest = Body(),
):
    if await transactions_crud.get_by_hash(payload.txn_hash):
        logger.info(f"Transaction {payload.txn_hash} already exists")
        return StoreTransactionResponse(ok=True)

    if not (project := await projects_crud.find_by_id_or_slug(payload.project_id)):
        return StoreTransactionResponse(ok=False, error="Project not found")

    try:
        receipt = await crypto.get_txn_receipt(
            chain_id=payload.chain_id,
            tx_hash=payload.txn_hash,
        )
    except TransactionNotFound:
        return StoreTransactionResponse(ok=False, error="Transaction not found")
    except KeyError:
        return StoreTransactionResponse(ok=False, error="Invalid chain_id")

    if receipt["from"].lower() != payload.user_address.lower():
        return StoreTransactionResponse(ok=False, error="Invalid sender")

    if receipt["status"] != 1:
        try:
            await crypto.wait_for_txn_receipt(
                chain_id=payload.chain_id,
                tx_hash=payload.txn_hash,
            )
        except TimeExhausted:
            return StoreTransactionResponse(ok=False, error="Transaction failed")

    block_number = receipt["blockNumber"]

    if project.project_type == ProjectType.DEFAULT:
        if receipt["to"].lower() != settings.launchpad_contract_address.lower():
            return StoreTransactionResponse(ok=False, error="Invalid recipient")

        monitor_and_save_launchpad_events.apply_async(
            kwargs={
                "from_block": block_number,
                "to_block": block_number,
                "chain_id": payload.chain_id,
                "project_id": project.id,
            },
            countdown=1,
        )
    elif project.project_type == ProjectType.PRIVATE_PRESALE:
        if not (project_proxy_url := project.proxy_link.base_url):
            logger.error(f"Project {project.slug} has no proxy_url to store transaction")
            return StoreTransactionResponse(ok=False, error="Invalid proxy_url")
        project_contracts: dict[str, str] | None = await get_data_with_cache(
            key=f"project_contracts_{project.slug}",
            func=partial(get_crypto_contracts, project_proxy_url),
            redis=redis,
            short_key_exp_seconds=60,
            long_key_exp_minutes=60,
        )
        if not project_contracts:
            return StoreTransactionResponse(ok=False, error="Invalid proxy_url")
        str_network = crypto.get_network_by_chain_id(payload.chain_id)
        if not str_network:
            return StoreTransactionResponse(ok=False, error="Invalid chain_id")

        contract = project_contracts.get(str_network)
        if not contract:
            return StoreTransactionResponse(
                ok=False, error=f"Invalid chain_id, can't get contract from {project_contracts=}"
            )
        if receipt["to"].lower() != contract.lower():
            return StoreTransactionResponse(ok=False, error="Invalid recipient")

        monitor_and_save_multichain_launchpad_events.apply_async(
            kwargs={
                "from_block": block_number,
                "to_block": block_number,
                "chain_id": payload.chain_id,
                "contract_address": contract,
                "project_id": project.id,
            },
            countdown=1,
        )

    return StoreTransactionResponse(ok=True)
