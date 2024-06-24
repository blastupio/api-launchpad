import asyncio
from math import ceil

from fastapi import APIRouter, Path, Query, Body
from fastapi_pagination import Page
from starlette.responses import JSONResponse
from web3 import Web3

from app.base import logger
from app.consts import NATIVE_TOKEN_ADDRESS
from app.dependencies import (
    LaunchpadProjectCrudDep,
    SupportedTokensCrudDep,
    ProfileCrudDep,
    RefcodesCrudDep,
    CryptoDep,
    RedisDep,
)
from app.limiter import limiter

from app.schema import (
    TierInfoResponse,
    UserInfoResponse,
    ChainId,
    TokenInChain,
    TokenPriceResponse,
    Any2AnyPriceResponse,
    RatesForChainAndToken,
    InternalServerError,
    ErrorResponse,
    YieldPercentageResponse,
    GetUserProjectsResponse,
    RefcodeResponse,
    SaveReferrerResponse,
    CreateProfilePayload,
    CreateProfileResponse,
    CreateProfileResponseData,
    LeaderboardResponse,
)
from app.services.balances.blastup_balance import get_blastup_tokens_balance_for_chains
from app.services.ido_staking.tvl import get_ido_staking_daily_reward_for_user
from app.services.prices import get_tokens_price_for_chain, get_any2any_prices
from app.services.prices.cache import token_price_cache
from app.services.referral_system.referrals import get_n_referrals
from app.services.tiers.consts import (
    bronze_tier,
    silver_tier,
    gold_tier,
    titanium_tier,
    platinum_tier,
    diamond_tier,
)
from app.services.tiers.user_tier import get_user_tier
from app.services.user_projects import get_user_registered_projects
from app.services.yield_apr import get_native_yield, get_stablecoin_yield
from fastapi import Request

from app.utils import get_data_with_cache

router = APIRouter(prefix="/info", tags=["info"])


@router.get("/token-price", response_model=TokenPriceResponse, description="Get token price in USD")
async def get_token_price(
    chain_id: ChainId = Query(..., example=1),
    token_addresses: str = Query(
        description="comma-separated list of token addresses",
        example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2,0x0000000000000000000000000000000000000000",  # noqa
    ),
) -> TokenPriceResponse:
    _list_tokens_addresses = token_addresses.split(",")
    filtered_list_tokens_addresses = list(
        {
            address
            for address in _list_tokens_addresses
            if Web3.is_address(address) or address == NATIVE_TOKEN_ADDRESS
        }
    )
    if not filtered_list_tokens_addresses:
        return TokenPriceResponse(price={})
    prices = await get_tokens_price_for_chain(
        chain_id=chain_id, token_addresses=filtered_list_tokens_addresses
    )
    return TokenPriceResponse(price=prices)


@router.post("/any2any-price", response_model=Any2AnyPriceResponse)
async def get_any2any_price_rate(
    from_token: TokenInChain, to_tokens: list[TokenInChain]
) -> Any2AnyPriceResponse:
    if not to_tokens:
        return Any2AnyPriceResponse(rate=RatesForChainAndToken({}))
    rates = await get_any2any_prices(from_token, to_tokens)
    return Any2AnyPriceResponse(rate=rates)


@router.get("/user/{address}", response_model=UserInfoResponse | ErrorResponse)
async def get_user_info(
    profile_crud: ProfileCrudDep,
    refcodes_crud: RefcodesCrudDep,
    crypto_launchpad: CryptoDep,
    redis: RedisDep,
    address: str = Path(
        pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"
    ),
):
    if (profile := await profile_crud.first_by_address(address)) is None:
        return JSONResponse(content={"ok": False, "error": "Profile not found"}, status_code=404)

    # Retrieve user's tier based on BLP staking value
    # We check BLPStaking and LockedBLPStaking contracts
    async def get_blp_staked():
        try:
            blp_staked_balance = await crypto_launchpad.get_blp_staking_value(address)
        except Exception as e:
            logger.error(f"Cannot get blp staked balance for {address}: {e}")
            return None
        return blp_staked_balance

    blp_staked_balance = await get_data_with_cache(
        key=f"blp_staked_balance_{address.lower()}",
        func=get_blp_staked,
        redis=redis,
    )
    if blp_staked_balance is None:
        return InternalServerError("Failed to get staked BLP data")

    async def get_balance_by_chain_id():
        # Retrieve user's BLP balance via all chains from Presale contracts
        try:
            balances_by_chain_id = await get_blastup_tokens_balance_for_chains(address)
        except Exception as e:
            logger.error(f"Cannot get balance for {address}: {e}")
            return None
        return balances_by_chain_id

    balances_by_chain_id = await get_data_with_cache(
        key=f"balance_by_chain_id_{address.lower()}",
        func=get_balance_by_chain_id,
        redis=redis,
    )
    if blp_staked_balance is None:
        return InternalServerError("Failed to get BLP balance by chain id")

    refcode, n_referrals, leaderboard_rank, ido_daily_reward = await asyncio.gather(
        refcodes_crud.generate_refcode_if_not_exists(address),
        get_n_referrals(address, profile_crud),
        profile_crud.get_leaderboard_rank(address),
        get_ido_staking_daily_reward_for_user(address),
    )

    return UserInfoResponse(
        tier=get_user_tier(blp_staked_balance),
        blastup_balance=balances_by_chain_id,
        points=profile.points,
        terms_accepted=profile.terms_accepted,
        refcode=refcode.refcode,
        ref_points=profile.ref_points,
        n_referrals=n_referrals,
        referrer=profile.referrer,
        ref_bonus_used=profile.ref_bonus_used,
        leaderboard_rank=leaderboard_rank,
        ido_daily_reward=ido_daily_reward,
    )


@router.post("/user", response_model=CreateProfileResponse)
async def create_profile(
    profile_crud: ProfileCrudDep,
    payload: CreateProfilePayload,
):
    profile, is_new = await profile_crud.get_or_create_profile(
        address=payload.address,
        utm=payload.utm,
        language=payload.language,
        first_login=payload.first_login,
        browser=payload.browser,
    )
    return CreateProfileResponse(data=CreateProfileResponseData(is_new=is_new))


@router.post("/user/refcode", response_model=RefcodeResponse)
async def create_refcode(
    refcodes_crud: RefcodesCrudDep,
    address: str = Body(embed=True, pattern="^(0x)[0-9a-fA-F]{40}$"),
):
    refcode = await refcodes_crud.generate_refcode_if_not_exists(address)
    return RefcodeResponse(ok=True, data=refcode.refcode)


@router.post("/user/{address}/referrer", response_model=SaveReferrerResponse)
async def save_referrer_for_user(
    refcodes_crud: RefcodesCrudDep,
    profile_crud: ProfileCrudDep,
    address: str = Path(pattern="^(0x)[0-9a-fA-F]{40}$"),
    refcode: str = Body(embed=True, min_length=4, max_length=4),
):
    if not (referrer := await refcodes_crud.get_by_refcode(refcode)):
        return JSONResponse(content={"ok": False, "error": "Referrer not found"}, status_code=404)

    if referrer.address.lower() == address.lower():
        return JSONResponse(
            content={"ok": False, "error": "Referrer cannot be the same as the user"},
            status_code=400,
        )

    if not (profile := await profile_crud.first_by_address(address)):
        # create new profile with referrer
        await profile_crud.get_or_create_profile(address=address, referrer=referrer.address)
        return SaveReferrerResponse(ok=True)

    if profile.referrer:
        return JSONResponse(
            content={"ok": False, "error": "User already has a referrer"}, status_code=400
        )

    await profile_crud.update_referrer(address=address, referrer=referrer.address)
    return SaveReferrerResponse(ok=True)


@router.get("/tiers", response_model=TierInfoResponse)
async def get_all_tiers():
    return {
        "tiers": [bronze_tier, silver_tier, gold_tier, titanium_tier, platinum_tier, diamond_tier]
    }


@router.get("/yield-percentage", response_model=YieldPercentageResponse)
async def get_yield_percentage() -> YieldPercentageResponse:
    native_yield, stablecoin_yield = await asyncio.gather(
        get_native_yield(), get_stablecoin_yield()
    )
    return YieldPercentageResponse(native=native_yield, stablecoin=stablecoin_yield)


@router.get("/user-projects/{user_address}", response_model=GetUserProjectsResponse)
async def get_user_projects(
    projects_crud: LaunchpadProjectCrudDep,
    user_address: str = Path(
        pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"
    ),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=30, ge=3, le=30),
):
    projects, total_rows = await get_user_registered_projects(
        projects_crud, user_address, page, size
    )
    total_pages = ceil(total_rows / size)
    page = Page(total=total_rows, page=page, size=size, items=projects, pages=total_pages)
    return GetUserProjectsResponse(data=page)


@router.get("/supported-tokens")
async def get_supported_tokens(tokens_crud: SupportedTokensCrudDep):
    last_updated_at, rows = await asyncio.gather(
        token_price_cache.get_token_price_cache_updated_at(), tokens_crud.get_supported_tokens()
    )
    token_addresses_by_chain_id = {}
    for row in rows:
        token_addresses_by_chain_id.setdefault(row.chain_id, []).append(row.token_address)

    return {"tokens": token_addresses_by_chain_id, "cache_updated_at": last_updated_at}


@router.get("/leaderboard", response_model=LeaderboardResponse | ErrorResponse)
@limiter.limit("5/minute")
@limiter.limit("1/second")
async def leaderboard(request: Request, profile_crud: ProfileCrudDep):
    results = await profile_crud.get_top_by_points()
    return LeaderboardResponse(data=results)
