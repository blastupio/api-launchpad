from telegram import Bot
from web3 import Web3

from app import chains
from app.base import logger
from app.consts import NATIVE_TOKEN_ADDRESS
from app.dependencies import get_munzen
from app.env import settings
from app.models import OnRampOrder
from app.services.prices import get_tokens_price_for_chain


class NotificationBot:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token)
        self.chat_id = chat_id

    async def send(self, message: str) -> None:
        logger.info(f"NotificationBot:\nSending message: {message}")
        env_prefix = "🧑‍💻<b>DEV</b>" if settings.app_env == "dev" else ""
        message = f"{env_prefix} {message}"
        await self.bot.send_message(
            self.chat_id, message, parse_mode="HTML", disable_web_page_preview=True
        )

    async def send_low_onramp_bridge_balance(
        self, blast_balance: float, usd_balance: float
    ) -> None:
        address = settings.onramp_sender_addr
        blast_scan_url = f"https://blastscan.io/address/{address}"
        msg = (
            f"⚠️ Onramp Bridge <b>Warning</b>\n\n"
            f"Balance is low\n"
            f"Balance: <b>{blast_balance:.6f}</b> ETH (<b>${usd_balance:.2f}</b>)\n"
            f"<b>Wallet</b>: <code>{address}</code>\n"
            f"<a href='{blast_scan_url}'>(Contract)</a>"
        )
        await self.send(msg)

    async def completed_onramp_order(
        self,
        order: OnRampOrder,
        wei_balance_after_txn: int,
    ) -> None:
        scanner_prefix = "sepolia." if settings.app_env == "dev" else ""
        scanner_url = f"https://{scanner_prefix}blastscan.io/tx/{order.hash}"

        munzen_bridge_transaction = "Can't get munzen transaction"
        if munzen_order_id := order.munzen_order_id:
            try:
                munzen = get_munzen()
                order_data = (await munzen.get_order_data(munzen_order_id)).get("result")
                munzen_txn_hash = order_data.get("blockchainNetworkTxId", "")
                munzen_txn_url = f"https://{scanner_prefix}etherscan.io/tx/{munzen_txn_hash}"
                short_hash = f"{munzen_txn_hash[:6]}...{munzen_txn_hash[-6:]}"
                munzen_bridge_transaction = f"<a href='{munzen_txn_url}'>{short_hash}</a>"
            except Exception as e:
                logger.error(f"Can't get munzen order data: {e}")
        balance = float(Web3.from_wei(wei_balance_after_txn, "ether"))

        _eth_price = await get_tokens_price_for_chain(chains.blast.id, [NATIVE_TOKEN_ADDRESS])
        eth_price = _eth_price.get(NATIVE_TOKEN_ADDRESS)
        dollar_balance = round(balance * eth_price, 2) if eth_price else "unknown"

        if order.currency == "USD":
            amount = float(order.amount) / 100
            str_amount = f"${amount:.2f}"
        else:
            amount = Web3.from_wei(int(order.amount), "ether")
            dollar_amount = round(amount * eth_price, 2) if eth_price else "unknown"
            str_amount = f"{amount:.6f} ETH (${dollar_amount})"

        if order.hash:
            short_hash = f"{order.hash[:6]}...{order.hash[-6:]}"
        else:
            short_hash = "null hash"
        user_bridge_transaction = f"<a href='{scanner_url}'>{short_hash}</a>"
        msg = (
            f"<b>✅ COMPLETED Munzen Order</b>\n\n"
            f"<b>ID:</b> {order.id}\n"
            f"<b>Amount:</b> {str_amount}\n"
            f"<b>Munzen -> Bridge:</b> {munzen_bridge_transaction}\n"
            f"<b>Bridge -> User:</b> {user_bridge_transaction}\n"
            f"<b>Onramp wallet balance:</b> {balance:.6f} ETH (${dollar_balance})"
        )
        await self.send(msg)

    async def onramp_order_failed(self, order_id: str, balance_wei: int, error_msg: str) -> None:
        balance = float(Web3.from_wei(balance_wei, "ether"))
        msg = (
            f"<b>❌ FAILED Munzen Order</b>\n\n"
            f"<b>ID:</b> {order_id}\n"
            f"<b>Error:</b> <code>{error_msg}</code>\n\n"
            f"<b>Onramp wallet balance:</b> {balance:.6f} ETH"
        )
        await self.send(msg)


notification_bot = NotificationBot(
    settings.tg_bot_notification_token, settings.tg_notification_chat_id
)
