import traceback

from celery import Celery
from celery.exceptions import Retry

from app.base import logger
from app.common import run_command_and_get_result
from app.env import settings
from app.services.stake_history.jobs import ProcessHistoryStakingEvent
from app.services.total_raised.jobs import RecalculateProjectsTotalRaised
from app.tg_notifications.jobs import (
    TelegramNotifyCompletedOnrampTransaction,
    TelegramNotifyErrorOnrampTransaction,
)
from onramp.jobs import ProcessMunzenOrder, MonitorSenderBalance

app = Celery("tasks", broker=settings.celery_broker)


@app.task(
    max_retries=10,
    default_retry_delay=15,
)
def process_munzen_order(entity_id: str):
    try:
        result = run_command_and_get_result(ProcessMunzenOrder(entity_id, app))

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            process_munzen_order.apply_async(args=[entity_id], countdown=retry_after)
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(
            f"process_munzen_order[{entity_id}] Unhandled exception: {e}, {traceback.format_exc()}"
        )
        raise Retry("", exc=e)


@app.task(
    max_retries=5,
    default_retry_delay=15,
)
def process_history_staking_event():
    try:
        result = run_command_and_get_result(ProcessHistoryStakingEvent())

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            process_history_staking_event.apply_async(countdown=retry_after)
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(
            f"process_history_staking_event. Unhandled exception: {e}, {traceback.format_exc()}"
        )
        raise Retry("", exc=e)


@app.task(max_retries=3)
async def recalculate_project_total_raised():
    try:
        command = RecalculateProjectsTotalRaised()
        result = await command.run()

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            recalculate_project_total_raised.apply_async(countdown=retry_after)
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(
            f"recalculate_project_total_raised Unhandled exception: {e}, {traceback.format_exc()}"
        )
        raise Retry("", exc=e)


@app.task(max_retries=3, default_retry_delay=10)
async def monitor_onramp_bridge_balance():
    try:
        command = MonitorSenderBalance()
        result = await command.run()

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            monitor_onramp_bridge_balance.apply_async(countdown=retry_after)
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(
            f"monitor_onramp_bridge_balance Unhandled exception: {e}, {traceback.format_exc()}"
        )
        raise Retry("", exc=e)


@app.task(
    max_retries=3,
    default_retry_delay=15,
)
async def telegram_notify_completed_transaction(entity_id: str, wei_balance_after_txn: int):
    try:
        result = await TelegramNotifyCompletedOnrampTransaction(
            entity_id, wei_balance_after_txn
        ).run()

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            telegram_notify_completed_transaction.apply_async(
                args=[entity_id, wei_balance_after_txn], countdown=retry_after
            )
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(
            f"telegram_notify_completed_transaction[{entity_id}] "
            f"Unhandled exception: {e}, {traceback.format_exc()}"
        )
        raise Retry("", exc=e)


@app.task(
    max_retries=3,
    default_retry_delay=15,
)
async def telegram_notify_failed_transaction(entity_id: str, wei_balance: int, error: str):
    try:
        result = await TelegramNotifyErrorOnrampTransaction(entity_id, wei_balance, error).run()

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            telegram_notify_failed_transaction.apply_async(
                args=[entity_id, wei_balance, error], countdown=retry_after
            )
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(
            f"telegram_notify_failed_transaction[{entity_id}] "
            f"Unhandled exception: {e}, {traceback.format_exc()}"
        )
        raise Retry("", exc=e)
