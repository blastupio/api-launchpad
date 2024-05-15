from telegram import Bot
from web3 import Web3

from app.base import logger
from app.env import settings


class NotificationBot:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token)
        self.chat_id = chat_id

    async def send(self, message: str) -> None:
        logger.info(f"NotificationBot:\nSending message: {message}")
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
        self, order_id: str, tx_hash: str, munzen_txn_hash: str, balance_after_txn: int
    ) -> None:
        scanner_url = f"https://blastscan.io/tx/{tx_hash}"
        munzen_scanner_url = f"https://etherscan.io/tx/{munzen_txn_hash}"
        balance = float(Web3.from_wei(balance_after_txn, "ether"))
        msg = (
            f"<b>✅ COMPLETED Munzen Order</b>\n\n"
            f"<b>ID:</b> {order_id}\n"
            f"<b>Transaction Munzen -> Bridge:</b> <a href='{munzen_scanner_url}'>tx_hash</a>\n"
            f"<b>Transaction Bridge -> User:</b> <a href='{scanner_url}'>tx_hash</a>\n"
            f"<b>Onramp wallet balance:</b> {balance:.6f} ETH"
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
