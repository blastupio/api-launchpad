from uuid import UUID

from fastapi import Depends

from app.base import logger
from app.common import Command, CommandResult
from app.crud import OnRampCrud
from app.dependencies import get_onramp_crud
from app.services.tg_notifications.cli import notification_bot


class TelegramNotifyCompletedOnrampTransaction(Command):
    def __init__(self, order_id: str, wei_balance_after_txn: int):
        self.order_id = order_id
        self.wei_balance_after_txn = wei_balance_after_txn

    async def command(
        self,
        crud: OnRampCrud = Depends(get_onramp_crud),
    ) -> CommandResult:
        try:
            order = await crud.find_by_id(UUID(self.order_id))
            await notification_bot.completed_onramp_order(
                order=order, wei_balance_after_txn=self.wei_balance_after_txn
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram notification for order {self.order_id}: {e}")
            return CommandResult(success=False, need_retry=True, retry_after=1)
        return CommandResult(success=True)


class TelegramNotifyErrorOnrampTransaction(Command):
    def __init__(self, order_id: str, wei_balance: int, error: str):
        self.order_id = order_id
        self.wei_balance = wei_balance
        self.error = error

    async def command(
        self,
        crud: OnRampCrud = Depends(get_onramp_crud),
    ) -> CommandResult:
        try:
            order = await crud.find_by_id(UUID(self.order_id))
            await notification_bot.onramp_order_failed(
                order=order, balance_wei=self.wei_balance, error=self.error
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram notification for order {self.order_id}: {e}")
            return CommandResult(success=False, need_retry=True, retry_after=1)
        return CommandResult(success=True)
