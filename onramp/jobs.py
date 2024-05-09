import asyncio
from uuid import UUID

from fastapi import Depends

from app.base import logger
from app.common import Command, CommandResult
from app.crud import OnRampCrud
from app.dependencies import get_lock, get_onramp_crud, get_crypto
from app.models import ONRAMP_STATUS_COMPLETE
from app.services import Lock
from app.tg import notification_bot
from onramp.services import Crypto


class ProcessMunzenOrder(Command):
    def __init__(self, order_id: str):
        self.order_id = order_id

    async def command(
        self,
        lock: Lock = Depends(get_lock),
        crud: OnRampCrud = Depends(get_onramp_crud),
        crypto: Crypto = Depends(get_crypto),
    ) -> CommandResult:
        if not await lock.acquire("is-ready:munzen-processing"):
            logger.debug(f"[ProcessMunzenOrder({self.order_id})] Another order in progress")
            return CommandResult(success=False, need_retry=True, retry_after=10)

        if not await lock.acquire(f"munzen-order:{self.order_id}"):
            return CommandResult(success=False, need_retry=True, retry_after=60)

        try:
            order = await crud.get_by_id(UUID(self.order_id))
            if order.status == ONRAMP_STATUS_COMPLETE:
                logger.info(f"[ProcessMunzenOrder({self.order_id})] Order already completed")
                return CommandResult(success=False, need_retry=False)

            balance = await crypto.get_sender_balance()
            try:
                if tx_hash := await crypto.send_eth(order.address, order.received_amount):
                    order.status = ONRAMP_STATUS_COMPLETE
                    order.hash = tx_hash
                    await crud.persist(order)
                    balance_after_txn = balance - int(order.received_amount)
                    asyncio.create_task(
                        notification_bot.completed_onramp_order(
                            order_id=self.order_id,
                            tx_hash=tx_hash,
                            munzen_txn_hash=order.munzen_txn_hash,
                            balance_after_txn=balance_after_txn,
                        )
                    )
                    return CommandResult(success=True)
            except Exception as e:
                err = f"[ProcessMunzenOrder({self.order_id})] Cannot send order: {e}"
                logger.error(err)
                asyncio.create_task(
                    notification_bot.onramp_order_failed(
                        order_id=self.order_id, balance_wei=balance, error=err
                    )
                )
                return CommandResult(success=False, need_retry=True, retry_after=60)
        finally:
            await lock.release(f"munzen-order:{self.order_id}")
            await lock.release(f"munzen-order:{self.order_id}")
