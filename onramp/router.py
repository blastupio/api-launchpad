import json
from uuid import UUID

from fastapi import APIRouter, Depends, Body, HTTPException, Path

from app.base import logger
from app.crud import OnRampCrud
from app.dependencies import get_onramp_crud, get_munzen
from app.env import ONRAMP_RECIPIENT_ADDR
from app.models import OnRampOrder, ONRAMP_STATUS_NEW, ONRAMP_STATUS_COMPLETE, ONRAMP_STATUS_ERROR
from app.tasks import process_munzen_order
from app.utils import validation_error
from onramp.services import Munzen
from onramp.schema import OnRampPayload, OnRampResponse, OnRampResponseData, OnrampOrderResponse, ErrorResponse

router = APIRouter(prefix="/onramp", tags=["onramp"])


@router.get("/order/{order_id}", response_model=OnrampOrderResponse | ErrorResponse)
async def get_order_data(munzen: Munzen = Depends(get_munzen), order_id: UUID = Path()):
    try:
        order_data = (await munzen.get_order_data(str(order_id))).get("result")
    except Exception as e:
        if str(e) == "API Error. Status code: 404":
            return {"ok": False, "error": "Not found"}
        raise e

    if order_data.get("status") == "complete" and order_data.get("toWallet", "").lower() == ONRAMP_RECIPIENT_ADDR.lower():
        process_munzen_order.apply_async(args=[order_data.get("merchantOrderId")])

    return {"ok": True, "data": order_data}


@router.post("/payment-link", response_model=OnRampResponse)
async def get_payment_link(
        crud: OnRampCrud = Depends(get_onramp_crud),
        munzen: Munzen = Depends(get_munzen),
        payload: OnRampPayload = Body(embed=False)
):
    amount = 0.
    if payload.amount:
        try:
            amount = float(payload.amount)
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")
        except ValueError:
            raise validation_error(error_message="Invalid amount", location=("body", "amount"))

    if amount < 0.0062:  # 20 eur
        raise validation_error(error_message="Amount should be greater than 20 eur equivalent",
                               location=("body", "amount"))

    order = await crud.persist(OnRampOrder(
        amount=f"{int(amount * 1e18)}",
        currency="ETH",
        status=ONRAMP_STATUS_NEW,
        address=payload.address.lower(),
    ))

    payment_link = await munzen.generate_link(order.id, f"{amount:.8f}", order.currency)
    return OnRampResponse(ok=True, data=OnRampResponseData(
        internal_uuid=str(order.id),
        link=payment_link
    ))


@router.post("/webhook", include_in_schema=False)
async def webhook_handler(munzen: Munzen = Depends(get_munzen),
                          crud: OnRampCrud = Depends(get_onramp_crud),
                          payload: dict = Body(embed=True, alias="data"),
                          signature: str = Body(embed=True)):
    if not await munzen.validate_webhook(payload, signature):
        raise HTTPException(detail="Invalid signature", status_code=400)

    order = await crud.get_by_id(UUID(payload.get("merchantOrderId")))
    if not order:
        raise HTTPException(detail="Order not found", status_code=404)

    logger.info(f"[onramp webhook] Received webhook: {json.dumps(payload)}")
    if payload.get('eventType') == "order_failed" and order.status not in [ONRAMP_STATUS_COMPLETE, ONRAMP_STATUS_ERROR]:
        order.status = ONRAMP_STATUS_ERROR
        order.extra = payload
        await crud.persist(order)

    if payload.get('eventType') == "order_complete" and order.status != ONRAMP_STATUS_COMPLETE:
        logger.info(f"[onramp webhook] Scheduled job for id {order.id}")
        process_munzen_order.apply_async(args=[str(order.id)])

    return {"ok": True}
