import json
from uuid import UUID

from fastapi import APIRouter, Depends, Body, HTTPException, Path

from app.base import logger
from app.crud import OnRampCrud
from app.dependencies import get_onramp_crud, get_munzen, get_amount_converter
from app.env import settings
from app.models import OnRampOrder, ONRAMP_STATUS_NEW, ONRAMP_STATUS_COMPLETE, ONRAMP_STATUS_ERROR
from app.tasks import process_munzen_order
from app.types import MunzenWebhookEvent, MunzenOrderType
from app.utils import validation_error
from onramp.services import Munzen, AmountConverter
from onramp.schema import (
    OnRampPayload,
    OnRampResponse,
    OnRampResponseData,
    OnrampOrderResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/onramp", tags=["onramp"])


@router.get("/order/{order_id}", response_model=OnrampOrderResponse | ErrorResponse)
async def get_order_data(
    crud: OnRampCrud = Depends(get_onramp_crud),
    munzen: Munzen = Depends(get_munzen),
    order_id: UUID = Path(),
):
    try:
        order_data = (await munzen.get_order_data(str(order_id))).get("result")
    except Exception as e:
        if str(e) == "API Error. Status code: 404":
            return {"ok": False, "error": "Not found"}

        return {"ok": False, "error": str(e)}

    if (
        order_data.get("status") == "complete"
        and order_data.get("toWallet", "").lower() == settings.onramp_recipient_addr.lower()
    ):
        order = await crud.get_by_id(UUID(order_data.get("merchantOrderId")))
        if order:
            order.received_amount = f"{int(float(order_data.get('toAmount')) * 1e18)}"
            await crud.persist(order)
        process_munzen_order.apply_async(args=[order_data.get("merchantOrderId")], countdown=1)

    return {"ok": True, "data": order_data}


@router.post("/payment-link", response_model=OnRampResponse)
async def get_payment_link(
    crud: OnRampCrud = Depends(get_onramp_crud),
    munzen: Munzen = Depends(get_munzen),
    amount_converter: AmountConverter = Depends(get_amount_converter),
    payload: OnRampPayload = Body(embed=False),
):
    amount = 0.0
    if payload.amount:
        try:
            amount = float(payload.amount)
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
        except ValueError:
            raise validation_error(error_message="Invalid amount", location=("body", "amount"))

    currency = payload.currency
    if currency == "ETH" and await amount_converter.convert("ETH", amount) < 11:  # 11 usd
        raise validation_error(
            error_message="Amount should be greater than 11 usd equivalent",
            location=("body", "amount"),
        )
    if currency == "USD" and amount < 11:
        raise validation_error(
            error_message="Amount should be greater than 11 usd equivalent",
            location=("body", "amount"),
        )

    order = await crud.persist(
        OnRampOrder(
            amount=f"{int(amount * 1e18)}" if currency == "ETH" else f"{int(amount * 100)}",
            currency=currency,
            status=ONRAMP_STATUS_NEW,
            address=payload.recipient.lower(),
        )
    )

    amount_str = f"{amount:.8f}" if currency == "ETH" else f"{amount:.2f}"
    payment_link = await munzen.generate_link(order.id, amount_str, order.currency)
    return OnRampResponse(
        ok=True, data=OnRampResponseData(internal_uuid=str(order.id), link=payment_link)
    )


@router.post("/webhook", include_in_schema=False)
async def webhook_handler(
    munzen: Munzen = Depends(get_munzen),
    crud: OnRampCrud = Depends(get_onramp_crud),
    payload: dict = Body(embed=True, alias="data"),
    signature: str = Body(embed=True),
):
    payload: MunzenWebhookEvent

    if not await munzen.validate_webhook(payload, signature):
        logger.info(f"[onramp webhook] Invalid signature: {signature}")
        raise HTTPException(detail="Invalid signature", status_code=400)

    if not (order := await crud.get_by_id(UUID(payload.get("merchantOrderId")))):
        logger.info(f"[onramp webhook] Order not found: {payload.get('merchantOrderId')}")
        raise HTTPException(detail="Order not found", status_code=404)
    order.munzen_txn_hash = payload.get("blockchainNetworkTxId")

    logger.info(f"[onramp webhook] Received webhook: {json.dumps(payload)}")
    if payload.get("eventType") == MunzenOrderType.ORDER_FAILED.value and order.status not in [
        ONRAMP_STATUS_COMPLETE,
        ONRAMP_STATUS_ERROR,
    ]:
        order.status = ONRAMP_STATUS_ERROR
        order.extra = payload
        await crud.persist(order)

    if (
        payload.get("eventType") == MunzenOrderType.ORDER_COMPLETE.value
        and order.status != ONRAMP_STATUS_COMPLETE
    ):
        order.received_amount = f"{int(float(payload.get('toAmount')) * 1e18)}"
        await crud.persist(order)

        logger.info(f"[onramp webhook] Scheduled job for id {order.id}")
        process_munzen_order.apply_async(args=[str(order.id)], countdown=1)

    return {"ok": True}
