from telegram import Bot

from app.env import settings


notification_bot = Bot(settings.tg_bot_notification_token)
