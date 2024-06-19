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

    ido_sign_account_private_key: str | None = None  # todo: not None
    launchpad_contract_address: str | None = None  # todo: not None

    coingecko_api_key: str | None = None
    coingecko_errors_in_cache_minutes: int = 3

    price_errors_count_to_switch_to_long_cache: int = 10
    price_long_cache_minutes: int = 10

    eth_price_feed_addr: str

    munzen_environment: str = "sandbox"  # todo: use enum
    munzen_api_key: str = ""
    munzen_api_secret: str = ""

    onramp_recipient_addr: str
    onramp_sender_addr: str | None = None
    onramp_sender_seed_phrase: str
    onramp_usd_balance_threshold: int = 1000

    crypto_environment: str = "testnet"  # todo: use enum
    crypto_api_key_eth: str = ""
    crypto_api_key_polygon: str = ""
    crypto_api_key_bsc: str = ""
    crypto_api_key_blast: str = ""
    crypto_api_key_base: str = ""
    fallback_api_url_eth: str = ""
    fallback_api_url_bsc: str = ""
    fallback_api_url_polygon: str = ""
    fallback_api_url_blast: str = ""
    fallback_api_url_base: str = ""
    fallback_api_key_base: str = ""
    fallback_api_key_eth: str = ""
    fallback_api_key_bsc: str = ""
    fallback_api_key_polygon: str = ""
    fallback_api_key_blast: str = ""

    contract_addr_eth: str
    contract_addr_polygon: str
    contract_addr_bsc: str
    contract_addr_blast: str
    contract_addr_base: str | None = None  # todo: not None

    yield_staking_contract_addr: str | None = None  # todo: not None

    log_level: str = "DEBUG"  # todo: use enum

    proxy_base_url: str
    presale_api_url: str = "https://presale-api.blastup.io"

    tg_bot_notification_token: str
    tg_notification_chat_id: str

    blast_weth_address: str = "0x4300000000000000000000000000000000000004"
    blast_usdb_address: str = "0x4300000000000000000000000000000000000003"

    google_service_account_json: str | None = None
    google_launchpad_events_report_filename: str = "LaunchpadEvents"

    admin_project_name: str = ""

    ido_farming_participation_usd_threshold: float = 10

    staking_blp_oracle_contract: str
    staking_blp_contract_pool_1: str
    staking_blp_contract_pool_2: str
    staking_blp_contract_pool_3: str

    blp_balance_contract: str
    locked_blp_balance_contract: str


settings = Settings(_env_file=".env")


_log_level = settings.log_level
if _log_level not in ("CRITICAL", "FATAL", "ERROR", "WARNING", "INFO", "DEBUG"):
    _log_level = "INFO"

LOG_LEVEL = _log_level
