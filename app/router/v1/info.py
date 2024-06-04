import asyncio
from math import ceil

from fastapi import APIRouter, Path, Query, Body
from fastapi_pagination import Page
from web3 import Web3

from app.base import logger
from app.consts import NATIVE_TOKEN_ADDRESS
from app.dependencies import (
    LaunchpadProjectCrudDep,
    SupportedTokensCrudDep,
    ProfileCrudDep,
    RefcodesCrudDep,
)
from app.env import settings
from app.router.v1.proxy import fetch_data
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
)
from app.services.balances.blastup_balance import get_blastup_tokens_balance_for_chains
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
    address: str = Path(
        pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"
    ),
):
    try:
        balances_by_chain_id = await get_blastup_tokens_balance_for_chains(address)
    except Exception as e:
        logger.error(f"Cannot get balance for {address}: {e}")
        return InternalServerError("Failed to get user info")
    user_tier = get_user_tier(balances_by_chain_id)

    # todo: get from db after migration of presale
    url = f"{settings.presale_api_url}/users/profile/{address}"
    try:
        for _ in range(5):
            presale_json = await fetch_data(url, timeout=5)
            if presale_json["ok"]:
                break
            elif "not found" in presale_json["error"]:
                presale_json = {
                    "data": {"points": 0},
                    "ok": True,
                }
                break
    except Exception as e:
        logger.error(f"Can't get presale profile for {address}, {url=}: {e}")
        return InternalServerError(err="Can't get profile")

    presale_data = presale_json["data"]
    if profile := await profile_crud.first_by_address(address):
        presale_data["points"] += profile.points

    refcode, n_referrals = await asyncio.gather(
        refcodes_crud.generate_refcode_if_not_exists(address),
        get_n_referrals(address, profile_crud),
    )
    return UserInfoResponse(
        tier=user_tier,
        blastup_balance=balances_by_chain_id,
        refcode=refcode.refcode,
        n_referrals=n_referrals,
        **presale_data,
    )


@router.post("/user/refcode", response_model=RefcodeResponse)
async def create_refcode(
    refcodes_crud: RefcodesCrudDep,
    address: str = Body(embed=True, pattern="^(0x)[0-9a-fA-F]{40}$"),
):
    refcode = await refcodes_crud.generate_refcode_if_not_exists(address)
    return RefcodeResponse(ok=True, data=refcode.refcode)


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
