import traceback

from celery import Celery
from celery.exceptions import Retry

from app.base import logger
from app.common import run_command_and_get_result
from app.env import settings
from app.models import OperationType, OperationReason
from app.services.blp_staking.jobs import (
    AddBlpStakingPointsForProfile,
    AddBlpStakingPoints,
    MonitorBlpStakingLogsAndSave,
)
from app.services.ido_staking.jobs import (
    ProcessHistoryStakingEvent,
    AddIdoStakingPoints,
    AddIdoStakingPointsForProfile,
    MonitorIdoStakingLogsAndSave,
)
from app.services.launchpad.jobs import (
    MonitorLaunchpadLogsAndSave,
    SaveLaunchpadTransactionAndAddPoints,
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


@app.task(
    max_retries=5,
    default_retry_delay=15,
)
def monitor_and_save_blp_staking_events(
    from_block: int, to_block: int, chain_id: int, pool_id: int
):
    try:
        result = run_command_and_get_result(
            MonitorBlpStakingLogsAndSave(from_block, to_block, chain_id, pool_id)
        )

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            monitor_and_save_blp_staking_events.apply_async(
                args=[from_block, to_block, chain_id, pool_id], countdown=retry_after
            )
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e
        logger.error(
            f"monitor_and_save_blp_staking_events. Unhandled exception: {e}, {traceback.format_exc()}"  # noqa
        )
        raise Retry("", exc=e)


@app.task(
    max_retries=5,
    default_retry_delay=15,
)
def monitor_and_save_ido_staking_events(
    from_block: int,
    to_block: int,
    chain_id: int,
):
    try:
        result = run_command_and_get_result(
            MonitorIdoStakingLogsAndSave(from_block, to_block, chain_id)
        )

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            monitor_and_save_ido_staking_events.apply_async(
                args=[from_block, to_block, chain_id], countdown=retry_after
            )
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e
        logger.error(
            f"monitor_and_save_ido_staking_events. Unhandled exception: {e}, {traceback.format_exc()}"  # noqa
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
def add_ido_staking_points_for_profile(address: str, points_amount: int):
    try:
        result = run_command_and_get_result(
            AddIdoStakingPointsForProfile(
                address, points_amount, operation_type=OperationType.ADD_IDO_POINTS
            )
        )

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            logger.info(f"ido_staking_points[{address}] retrying after {retry_after}")
            add_ido_staking_points_for_profile.apply_async(
                args=[address, points_amount], countdown=retry_after
            )
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(f"ido_staking_points[{address}] error:{e}\n{traceback.format_exc()}")
        raise Retry("", exc=e)


@app.task(max_retries=3, default_retry_delay=10)
def add_referral_ido_staking_points_for_profile(
    address: str,
    points_amount: float,
    referring_profile_id: int | None = None,
):
    try:
        result = run_command_and_get_result(
            AddIdoStakingPointsForProfile(
                address,
                points_amount,
                referring_profile_id=referring_profile_id,
                operation_type=OperationType.ADD_REF,
                operation_reason=OperationReason.IDO_FARMING,
            )
        )

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            logger.info(f"ido_referral_staking_points[{address}] retrying after {retry_after}")
            add_referral_ido_staking_points_for_profile.apply_async(
                args=[address, points_amount, referring_profile_id], countdown=retry_after
            )
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(f"ido_referral_staking_points[{address}] error:{e}\n{traceback.format_exc()}")
        raise Retry("", exc=e)


@app.task(max_retries=3, default_retry_delay=10)
def add_blp_staking_points():
    try:
        result = run_command_and_get_result(AddBlpStakingPoints())

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            logger.info(f"add_blp_staking_points: retrying after {retry_after}")
            add_blp_staking_points.apply_async(countdown=retry_after)
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(f"add_blp_staking_points Unhandled exception: {e}, {traceback.format_exc()}")
        raise Retry("", exc=e)


@app.task(max_retries=3, default_retry_delay=10)
def add_blp_staking_points_for_profile(address: str, points_amount: int):
    try:
        result = run_command_and_get_result(
            AddBlpStakingPointsForProfile(
                address, points_amount, operation_type=OperationType.ADD_BLP_STAKING_POINTS
            )
        )

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            logger.info(f"blp_staking_points[{address}] retrying after {retry_after}")
            add_blp_staking_points_for_profile.apply_async(
                args=[address, points_amount], countdown=retry_after
            )
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(f"blp_staking_points[{address}] error:{e}\n{traceback.format_exc()}")
        raise Retry("", exc=e)


@app.task(max_retries=3, default_retry_delay=10)
def add_referral_blp_staking_points_for_profile(
    address: str,
    points_amount: float,
    referring_profile_id: int | None = None,
):
    try:
        result = run_command_and_get_result(
            AddBlpStakingPointsForProfile(
                address,
                points_amount,
                referring_profile_id=referring_profile_id,
                operation_type=OperationType.ADD_REF,
                operation_reason=OperationReason.BLP_STAKING,
            )
        )

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            logger.info(f"blp_referral_staking_points[{address}] retrying after {retry_after}")
            add_referral_blp_staking_points_for_profile.apply_async(
                args=[address, points_amount, referring_profile_id], countdown=retry_after
            )
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e

        logger.error(f"blp_referral_staking_points[{address}] error:{e}\n{traceback.format_exc()}")
        raise Retry("", exc=e)


@app.task(
    max_retries=5,
    default_retry_delay=15,
)
def monitor_and_save_launchpad_events(from_block: int, to_block: int, chain_id: int):
    try:
        result = run_command_and_get_result(
            MonitorLaunchpadLogsAndSave(from_block, to_block, chain_id)
        )

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            monitor_and_save_launchpad_events.apply_async(
                args=[from_block, to_block, chain_id], countdown=retry_after
            )
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e
        logger.error(
            f"monitor_and_save_launchpad_events. Unhandled exception: {e}, {traceback.format_exc()}"  # noqa
        )
        raise Retry("", exc=e)


@app.task(
    max_retries=5,
    default_retry_delay=15,
)
def save_launchpad_txn_and_add_points(
    user_address: str, txn_hash: str, contract_project_id: int, token_amount: int, chain_id: int
):
    try:
        result = run_command_and_get_result(
            SaveLaunchpadTransactionAndAddPoints(
                user_address, txn_hash, contract_project_id, token_amount, chain_id
            )
        )

        if result.need_retry:
            retry_after = (
                result.retry_after
                if result.retry_after is not None
                else settings.celery_retry_after
            )
            save_launchpad_txn_and_add_points.apply_async(
                args=[user_address, txn_hash, contract_project_id, token_amount, chain_id],
                countdown=retry_after,
            )
            return
    except Exception as e:
        if isinstance(e, Retry):
            raise e
        logger.error(
            f"save_launchpad_txn_and_add_points. Unhandled exception: {e}, {traceback.format_exc()}"  # noqa
        )
        raise Retry("", exc=e)
