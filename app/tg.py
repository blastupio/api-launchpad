from telegram import Bot

from app.env import settings


class NotificationBot:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token)
        self.chat_id = chat_id

    async def send(self, message: str) -> None:
        await self.bot.send_message(
            self.chat_id, message, parse_mode="HTML", disable_web_page_preview=True
        )

    async def send_low_onramp_bridge_balance(
        self, blast_balance: float, usd_balance: float
    ) -> None:
        blast_scan_url = f"https://blastscan.io/address/{settings.onramp_sender_addr}"
        msg = (
            f"<b>💸 WARNING 💸</b>\n\n"
            f"Onramp bridge balance is low\n"
            f"{blast_balance:.6f} BLAST (<b>${usd_balance:.2f}</b>)\n"
            f"<a href='{blast_scan_url}'>Contract</a>"
        )
        await self.send(msg)

    async def new_onramp_order(self, order_id: str, str_amount: str, currency: str) -> None:
        msg = (
            f"<b>🤑 NEW Munzen order 🤑</b>\n\n"
            f"<b>ID:</b> {order_id}\n"
            f"<b>Amount:</b> {str_amount} {currency}"
        )
        await self.send(msg)

    async def completed_onramp_order(self, order_id: str, tx_hash: str) -> None:
        scanner_url = f"https://blastscan.io/tx/{tx_hash}"
        msg = (
            f"<b>✅ Completed Munzen order ✅</b>\n\n"
            f"<b>ID:</b> {order_id}\n"
            f"<a href='{scanner_url}'>Transaction</a>"
        )
        await self.send(msg)

    async def onramp_order_failed(self, order_id: str, error_msg: str) -> None:
        msg = (
            f"<b> ❌ Failed Munzen order ❌ </b>\n\n"
            f"<b>ID:</b> {order_id}\n"
            f"<b>Error:</b> <code>{error_msg}</code>"
        )
        await self.send(msg)


notification_bot = NotificationBot(
    settings.tg_bot_notification_token, settings.tg_notification_chat_id
)
