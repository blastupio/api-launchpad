import asyncio
import traceback
from datetime import timedelta
from uuid import UUID

from celery import Celery
from fastapi import Depends
from web3 import Web3

from app.base import logger
from app.common import Command, CommandResult
from app.consts import NATIVE_TOKEN_ADDRESS
from app.crud import OnRampCrud
from app.dependencies import get_lock, get_onramp_crud, get_crypto, get_redis
from app.env import settings
from app.models import ONRAMP_STATUS_COMPLETE, OnRampOrder
from app.services import Lock
from app.services.prices import get_tokens_price_for_chain
from app.services.web3_nodes import web3_node
from app.services.tg_notifications.cli import notification_bot
from onramp.services import Crypto


class ProcessMunzenOrder(Command):
    def __init__(self, order_id: str, app: Celery | None = None):
        self.app = app
        self.order_id = order_id

    async def command(
        self,
        lock: Lock = Depends(get_lock),
        crud: OnRampCrud = Depends(get_onramp_crud),
        crypto: Crypto = Depends(get_crypto),
    ) -> CommandResult:
        order_lock_key = f"munzen-order:{self.order_id}"
        global_lock_key = "is-ready:munzen-processing"

        if not await lock.acquire(global_lock_key):
            logger.debug(f"[ProcessMunzenOrder({self.order_id})] Another order in progress")
            return CommandResult(success=False, need_retry=True, retry_after=10)

        if not await lock.acquire(order_lock_key):
            logger.debug(f"[ProcessMunzenOrder({self.order_id})] this order in progress")
            return CommandResult(success=False, need_retry=True, retry_after=60)

        try:
            order: OnRampOrder = await crud.find_by_id(UUID(self.order_id))
            if order.status == ONRAMP_STATUS_COMPLETE:
                logger.info(f"[ProcessMunzenOrder({self.order_id})] Order already completed")
                return CommandResult(success=False, need_retry=False)

            balance = await crypto.get_sender_balance()
            balance_after_txn = balance - int(order.received_amount)
            logger.info(
                f"[ProcessMunzenOrder({self.order_id})] Sending {order.received_amount} to {order.address}"  # noqa: E501
            )
            try:
                if tx_hash := await crypto.send_eth(order.address, order.received_amount):
                    order.status = ONRAMP_STATUS_COMPLETE
                    order.hash = tx_hash
                    await crud.persist(order)
                    logger.info(
                        f"[ProcessMunzenOrder({self.order_id})] Sent to {order.address}: {tx_hash}"
                    )
            except Exception as e:
                err = f"[ProcessMunzenOrder({self.order_id})] Cannot send order: {e}"
                logger.error(err)
                if self.app:
                    self.app.send_task(
                        "app.tasks.telegram_notify_failed_transaction",
                        (self.order_id, balance, err),
                        countdown=1,
                    )
                return CommandResult(success=False, need_retry=True, retry_after=60)
            else:
                if self.app:
                    self.app.send_task(
                        "app.tasks.telegram_notify_completed_transaction",
                        (self.order_id, balance_after_txn),
                        countdown=1,
                    )
                return CommandResult(success=True)
        finally:
            await lock.release(order_lock_key)
            await lock.release(global_lock_key)


class MonitorSenderBalance(Command):
    async def command(
        self,
    ) -> CommandResult:
        logger.info("Monitoring onramp bridge balance")
        redis = get_redis()

        if not settings.onramp_sender_addr:
            logger.warning("Onramp sender address is not set")
            return CommandResult(success=False, need_retry=False)

        try:
            web3 = await web3_node.get_web3("blast")
            chain_id = await web3.eth.chain_id
            balance_wei, balance_in_cache, blast_price = await asyncio.gather(
                web3.eth.get_balance(web3.to_checksum_address(settings.onramp_sender_addr)),
                redis.get("onramp_bridge_balance"),
                get_tokens_price_for_chain(
                    chain_id=chain_id, token_addresses=[NATIVE_TOKEN_ADDRESS]
                ),
            )
        except Exception as e:
            logger.error(
                f"monitor_onramp_bridge_balance. Unhandled exception: {e}, {traceback.format_exc()}"
            )
            return CommandResult(success=False, need_retry=True, retry_after=10)

        balance_in_cache = int(balance_in_cache) if balance_in_cache else 0
        if balance_wei == balance_in_cache:
            err = f"Monitoring onramp balance: balance in cache = blockchain balance: {balance_wei}"
            logger.info(err)
            return CommandResult(success=True)

        # balance has changed
        await redis.set("onramp_bridge_balance", balance_wei, ex=timedelta(hours=4))

        balance = float(Web3.from_wei(balance_wei, "ether"))
        if not (blast_usd_price := blast_price.get(NATIVE_TOKEN_ADDRESS)):
            logger.error(f"Can't get blast USD price for {NATIVE_TOKEN_ADDRESS}")
            return CommandResult(success=False, need_retry=True, retry_after=10)

        if (usd_balance := balance * blast_usd_price) < settings.onramp_usd_balance_threshold:
            if settings.app_env == "dev":
                msg = f"Onramp bridge balance is low: {balance:.6f} ETH ({usd_balance:.2f} USD)"
                logger.warning(msg)
            else:
                await notification_bot.send_low_onramp_bridge_balance(
                    blast_balance=balance,
                    usd_balance=usd_balance,
                )

        logger.info(
            f"Monitoring onramp bridge balance is done: {balance:.6f} ETH ({usd_balance:.2f} USD)"
        )
        return CommandResult(success=True)
