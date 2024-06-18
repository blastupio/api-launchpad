from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import async_session
from app.crud import OnRampCrud, LaunchpadProjectCrud
from app.crud.history_staking import HistoryStakingCrud
from app.crud.launchpad_events import LaunchpadContractEventsCrud
from app.crud.points import PointsHistoryCrud, ExtraPointsCrud
from app.crud.profiles import ProfilesCrud
from app.crud.project_whitelist import ProjectWhitelistCrud
from app.crud.refcodes import RefcodesCrud
from app.crud.supported_tokens import SupportedTokensCrud
from app.env import settings
from app.redis import redis_cli
from app.services import Lock, Crypto as CryptoLaunchpad
from app.services.points.add_points import AddPoints
from onramp.services import Munzen, Crypto, AmountConverter


def get_launchpad_crypto() -> CryptoLaunchpad:
    return CryptoLaunchpad(
        environment=settings.crypto_environment,
        contracts={
            "polygon": settings.contract_addr_polygon,
            "eth": settings.contract_addr_eth,
            "bsc": settings.contract_addr_bsc,
            "blast": settings.contract_addr_blast,
            "base": settings.contract_addr_base,
        },
        staking_oracle_contract=settings.staking_blp_oracle_contract,
        blp_balance_contract=settings.blp_balance_contract,
        locked_blp_balance_contract=settings.locked_blp_balance_contract,
    )


CryptoDep = Annotated[CryptoLaunchpad, Depends(get_launchpad_crypto)]


def get_redis() -> Redis:
    return redis_cli


RedisDep = Annotated[Redis, Depends(get_redis)]


async def get_lock(redis: Redis = Depends(get_redis)) -> Lock:
    return Lock(redis)


async def get_session() -> AsyncSession:
    async with async_session() as session, session.begin():
        yield session


async def get_launchpad_projects_crud(
    session: AsyncSession = Depends(get_session),
) -> LaunchpadProjectCrud:
    return LaunchpadProjectCrud(session)


async def get_staking_history_crud(
    session: AsyncSession = Depends(get_session),
) -> HistoryStakingCrud:
    return HistoryStakingCrud(session)


async def get_profile_crud(
    session: AsyncSession = Depends(get_session),
) -> ProfilesCrud:
    return ProfilesCrud(session)


async def get_points_history_crud(
    session: AsyncSession = Depends(get_session),
) -> PointsHistoryCrud:
    return PointsHistoryCrud(session)


async def get_extra_points_crud(
    session: AsyncSession = Depends(get_session),
) -> ExtraPointsCrud:
    return ExtraPointsCrud(session)


async def get_launchpad_contract_events_crud(
    session: AsyncSession = Depends(get_session),
) -> LaunchpadContractEventsCrud:
    return LaunchpadContractEventsCrud(session)


async def get_project_whitelist_crud(
    session: AsyncSession = Depends(get_session),
) -> ProjectWhitelistCrud:
    return ProjectWhitelistCrud(session)


async def get_supported_tokens_crud(
    session: AsyncSession = Depends(get_session),
) -> SupportedTokensCrud:
    return SupportedTokensCrud(session)


async def get_refcodes_crud(session: AsyncSession = Depends(get_session)) -> RefcodesCrud:
    return RefcodesCrud(session)


RefcodesCrudDep = Annotated[RefcodesCrud, Depends(get_refcodes_crud)]

HistoryStakingCrudDep = Annotated[HistoryStakingCrud, Depends(get_staking_history_crud)]

ProjectWhitelistCrudDep = Annotated[ProjectWhitelistCrud, Depends(get_project_whitelist_crud)]

LaunchpadProjectCrudDep = Annotated[LaunchpadProjectCrud, Depends(get_launchpad_projects_crud)]

SupportedTokensCrudDep = Annotated[SupportedTokensCrud, Depends(get_supported_tokens_crud)]

ProfileCrudDep = Annotated[ProfilesCrud, Depends(get_profile_crud)]

PointsHistoryCrudDep = Annotated[PointsHistoryCrud, Depends(get_points_history_crud)]

ExtraPointsCrudDep = Annotated[ExtraPointsCrud, Depends(get_extra_points_crud)]


async def get_onramp_crud(session: AsyncSession = Depends(get_session)) -> OnRampCrud:
    return OnRampCrud(session)


def get_munzen() -> Munzen:
    return Munzen(
        settings.munzen_api_key,
        settings.munzen_api_secret,
        settings.munzen_environment,
        settings.onramp_recipient_addr,
    )


async def get_crypto() -> Crypto:
    return Crypto(
        settings.crypto_api_key_blast,
        settings.onramp_sender_seed_phrase,
        settings.eth_price_feed_addr,
    )


async def get_amount_converter(
    redis: Redis = Depends(get_redis), crypto: Crypto = Depends(get_crypto)
) -> AmountConverter:
    return AmountConverter(redis, crypto)


async def get_add_points(
    profile_crud: ProfileCrudDep,
    points_history_crud: PointsHistoryCrudDep,
    extra_points_crud: ExtraPointsCrudDep,
) -> AddPoints:
    return AddPoints(profile_crud, points_history_crud, extra_points_crud)


AddPointsDep = Annotated[AddPoints, Depends(get_add_points)]
