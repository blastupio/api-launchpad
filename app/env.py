from os import getenv

from dotenv import load_dotenv

load_dotenv()

APP_ENV = getenv("APP_ENV", "dev")
APP_VERSION = getenv("APP_VERSION", "unstable")

SENTRY_DSN = getenv("SENTRY_DSN", None)
LOGTAIL_TOKEN = getenv("LOGTAIL_TOKEN")

ALLOWED_ORIGINS = getenv("ALLOWED_ORIGINS", "*").split(",")

DATABASE_URL = getenv("DATABASE_URL", "postgresql+asyncpg://blastup:blastup@postgres:5432/blastup")
REDIS_URL = getenv("REDIS_URL", "redis://localhost:6379")
CELERY_BROKER = getenv("CELERY_BROKER", "redis://localhost:6379/0")
CELERY_RETRY_AFTER = int(getenv("CELERY_RETRY_AFTER", "15"))

CRYPTO_API_KEY_BLAST = getenv("CRYPTO_API_KEY_BLAST", "")

# ONRAMP ONLY
ETH_PRICE_FEED_ADDR = getenv("ETH_PRICE_FEED_ADDR")

MUNZEN_ENVIRONMENT = getenv("MUNZEN_ENVIRONMENT", "sandbox")
MUNZEN_API_KEY = getenv("MUNZEN_API_KEY", "")
MUNZEN_API_SECRET = getenv("MUNZEN_API_SECRET", "")

ONRAMP_RECIPIENT_ADDR = getenv("ONRAMP_RECIPIENT_ADDR")
ONRAMP_SENDER_ADDR = getenv("ONRAMP_SENDER_ADDR")
ONRAMP_SENDER_SEED_PHRASE = getenv("ONRAMP_SENDER_SEED_PHRASE")
# ONRAMP ONLY

_log_level = getenv("LOG_LEVEL", "DEBUG")
if _log_level not in ("CRITICAL", "FATAL", "ERROR", "WARNING", "INFO", "DEBUG"):
    _log_level = "INFO"

LOG_LEVEL = _log_level
