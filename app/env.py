from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "dev"  # todo: use enum
    app_version: str = "unstable"

    sentry_dsn: str | None = None
    logtail_token: str | None = None
    allowed_origins: str = "*"

    database_url: PostgresDsn = "postgresql+asyncpg://launchpad:launchpad@localhost:5432/launchpad"
    redis_url: RedisDsn = "redis://localhost:6379"
    celery_broker: str = "redis://localhost:6379/0"
    celery_retry_after: int = 15

    controller_seed_phrase: str

    ido_sign_account_private_key: str | None = None  # todo: not None
    launchpad_contract_address: str | None = None  # todo: not None

    coingecko_api_key: str | None = None

    eth_price_feed_addr: str

    munzen_environment: str = "sandbox"  # todo: use enum
    munzen_api_key: str = ""
    munzen_api_secret: str = ""

    onramp_recipient_addr: str
    onramp_seed_phrase: str
    onramp_sender_addr: str | None = None
    onramp_sender_seed_phrase: str
    onramp_usd_balance_threshold: int = 1000

    usdt_contract_addr_eth: str
    usdt_contract_addr_bsc: str
    usdt_contract_addr_polygon: str
    usdt_contract_addr_blast: str

    crypto_environment: str = "testnet"  # todo: use enum
    crypto_api_key_eth: str = ""
    crypto_api_key_polygon: str = ""
    crypto_api_key_bsc: str = ""
    crypto_api_key_blast: str = ""
    fallback_api_url_eth: str = ""
    fallback_api_url_bsc: str = ""
    fallback_api_url_polygon: str = ""
    fallback_api_url_blast: str = ""
    fallback_api_key_eth: str = ""
    fallback_api_key_bsc: str = ""
    fallback_api_key_polygon: str = ""
    fallback_api_key_blast: str = ""

    contract_addr_eth: str
    contract_addr_polygon: str
    contract_addr_bsc: str
    contract_addr_blast: str

    yield_staking_contract_addr: str | None = None  # todo: not None

    log_level: str = "DEBUG"  # todo: use enum

    proxy_base_url: str

    tg_bot_notification_token: str
    tg_notification_chat_id: str

    google_service_account_json: str | None = None
    google_launchpad_events_report_filename: str = "LaunchpadEvents"


settings = Settings(_env_file=".env")


_log_level = settings.log_level
if _log_level not in ("CRITICAL", "FATAL", "ERROR", "WARNING", "INFO", "DEBUG"):
    _log_level = "INFO"

LOG_LEVEL = _log_level
