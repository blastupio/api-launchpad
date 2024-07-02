from fastapi import APIRouter, Body
from web3.exceptions import TransactionNotFound, TimeExhausted

from app.base import logger
from app.dependencies import CryptoDep, LaunchpadProjectCrudDep, TransactionsCrudDep
from app.env import settings
from app.models import ProjectType
from app.schema import StoreTransactionRequest, StoreTransactionResponse
from app.tasks import monitor_and_save_launchpad_events

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("")
async def store_transaction(
    transactions_crud: TransactionsCrudDep,
    projects_crud: LaunchpadProjectCrudDep,
    crypto: CryptoDep,
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

    if project.project_type == ProjectType.DEFAULT:
        if receipt["to"].lower() != settings.launchpad_contract_address.lower():
            return StoreTransactionResponse(ok=False, error="Invalid recipient")
    elif project.project_type == ProjectType.PRIVATE_PRESALE:
        pass

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
    monitor_and_save_launchpad_events.apply_async(
        kwargs={
            "from_block": block_number - 10,
            "to_block": block_number + 10,
            "chain_id": payload.chain_id,
        },
        countdown=1,
    )

    return StoreTransactionResponse(ok=True)
