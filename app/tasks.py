import traceback

from celery import Celery
from celery.exceptions import Retry

from app.base import logger
from app.common import run_command_and_get_result
from app.env import settings
from app.services.ido_staking.jobs import (
    ProcessHistoryStakingEvent,
    AddIdoStakingPoints,
    AddIdoStakingPointsForProfile,
)
from app.services.total_raised.jobs import RecalculateProjectsTotalRaised
from app.services.tg_notifications.jobs import (
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
def telegram_notify_completed_transaction(entity_id: str, wei_balance_after_txn: int):
    try:
        result = run_command_and_get_result(
            TelegramNotifyCompletedOnrampTransaction(entity_id, wei_balance_after_txn)
        )

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
def telegram_notify_failed_transaction(entity_id: str, wei_balance: int, error: str):
    try:
        result = run_command_and_get_result(
            TelegramNotifyErrorOnrampTransaction(entity_id, wei_balance, error)
        )

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


@app.task(max_retries=3, default_retry_delay=10)
def add_ido_staking_points():
    try:
        result = run_command_and_get_result(AddIdoStakingPoints())

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            logger.info(f"add_ido_staking_points: retrying after {retry_after}")
            add_ido_staking_points.apply_async(countdown=retry_after)
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(f"add_ido_staking_points Unhandled exception: {e}, {traceback.format_exc()}")
        raise Retry("", exc=e)


@app.task(max_retries=3, default_retry_delay=10)
def add_ido_staking_points_for_profile(profile_id: int, points_amount: int):
    try:
        result = run_command_and_get_result(
            AddIdoStakingPointsForProfile(profile_id, points_amount)
        )

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            logger.info(f"add_ido_staking_points[{profile_id}] retrying after {retry_after}")
            add_ido_staking_points.apply_async(countdown=retry_after)
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(
            f"add_ido_staking_points[{profile_id}], exception:{e}\n{traceback.format_exc()}"
        )
        raise Retry("", exc=e)
