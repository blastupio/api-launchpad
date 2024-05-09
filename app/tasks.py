import asyncio
import traceback
from datetime import timedelta

from celery import Celery
from celery.exceptions import Retry
from web3 import Web3

from app import chains
from app.base import logger
from app.common import run_command_and_get_result
from app.consts import NATIVE_TOKEN_ADDRESS
from app.dependencies import get_redis
from app.env import settings
from app.services.prices import get_tokens_price
from app.services.stake_history.jobs import ProcessHistoryStakingEvent
from app.services.total_raised.jobs import RecalculateProjectsTotalRaised
from app.services.web3_nodes import web3_node
from app.tg import notification_bot
from onramp.jobs import ProcessMunzenOrder

app = Celery("tasks", broker=settings.celery_broker)


@app.task(
    max_retries=10,
    default_retry_delay=15,
)
def process_munzen_order(entity_id: str):
    try:
        result = run_command_and_get_result(ProcessMunzenOrder(entity_id))

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
    logger.info("Monitoring onramp bridge balance")
    redis = get_redis()

    if not settings.onramp_sender_addr:
        logger.error("Onramp sender address is not set")
        return

    try:
        web3 = await web3_node.get_web3("blast")
        chain_id = await web3.eth.chain_id
        balance_wei, balance_in_cache, blast_price = await asyncio.gather(
            web3.eth.get_balance(web3.to_checksum_address(settings.onramp_sender_addr)),
            redis.get("onramp_bridge_balance"),
            get_tokens_price(chain_id=chain_id, token_addresses=[NATIVE_TOKEN_ADDRESS]),
        )
    except Exception as e:
        logger.error(
            f"monitor_onramp_bridge_balance. Unhandled exception: {e}, {traceback.format_exc()}"
        )
        return
    balance_in_cache = int(balance_in_cache) if balance_in_cache else 0
    if balance_wei == balance_in_cache:
        err = f"Monitoring onramp balance: balance in cache = blockchain balance: {balance_wei}"
        logger.info(err)
        return

    # balance has changed
    await redis.set("onramp_bridge_balance", balance_wei, ex=timedelta(hours=4))

    balance = float(Web3.from_wei(balance_wei, "ether"))
    if not (blast_usd_price := blast_price.get(NATIVE_TOKEN_ADDRESS)):
        logger.error(f"Can't get blast USD price for {NATIVE_TOKEN_ADDRESS}")
        monitor_onramp_bridge_balance.apply_async(countdown=10)
        return

    if (usd_balance := balance * blast_usd_price) < settings.onramp_usd_balance_threshold:
        if settings.app_env == "dev":
            msg = f"Onramp bridge balance is low: {balance:.6f} ETH ({usd_balance:.2f} USD)"
            logger.error(msg)
        else:
            await notification_bot.send_low_onramp_bridge_balance(
                blast_balance=balance,
                usd_balance=usd_balance,
            )
