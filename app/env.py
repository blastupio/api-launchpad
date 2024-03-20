from os import getenv

from dotenv import load_dotenv

load_dotenv()

APP_ENV = getenv("APP_ENV", "dev")

SENTRY_DSN = getenv("SENTRY_DSN", None)
LOGTAIL_TOKEN = getenv("LOGTAIL_TOKEN")

ALLOWED_ORIGINS = getenv("ALLOWED_ORIGINS", "*").split(",")

DATABASE_URL = getenv("DATABASE_URL", "postgresql+asyncpg://blastup:blastup@postgres:5432/blastup")
REDIS_URL = getenv("REDIS_URL", "redis://localhost:6379")
CELERY_BROKER = getenv("CELERY_BROKER", "redis://localhost:6379/0")
CELERY_RETRY_AFTER = int(getenv("CELERY_RETRY_AFTER", "15"))

_log_level = getenv("LOG_LEVEL", "DEBUG")
if _log_level not in ("CRITICAL", "FATAL", "ERROR", "WARNING", "INFO", "DEBUG"):
    _log_level = "INFO"

LOG_LEVEL = _log_level
