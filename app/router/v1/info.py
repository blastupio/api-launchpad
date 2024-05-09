import asyncio

from fastapi import APIRouter, Path, Query
from web3 import Web3

from app.base import logger
from app.consts import NATIVE_TOKEN_ADDRESS
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
)
from app.services.balances.blastup_balance import get_blastup_tokens_balance_for_chains
from app.services.tiers.consts import (
    bronze_tier,
    silver_tier,
    gold_tier,
    titanium_tier,
    platinum_tier,
    diamond_tier,
)
from app.services.tiers.user_tier import get_user_tier
from app.services.prices import get_tokens_price, get_any2any_prices
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
    filtered_list_tokens_addresses = [
        address
        for address in _list_tokens_addresses
        if Web3.is_address(address) or address == NATIVE_TOKEN_ADDRESS
    ]
    if not filtered_list_tokens_addresses:
        return TokenPriceResponse(price={})
    prices = await get_tokens_price(
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
    address: str = Path(
        pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"
    ),
):
    try:
        balances_by_chain_id = await get_blastup_tokens_balance_for_chains(address)
    except Exception as e:
        logger.error(f"Cannot get balance for {address}: {e}")
        return InternalServerError("Failed to get user info")
    else:
        user_tier = get_user_tier(balances_by_chain_id)
        return UserInfoResponse(tier=user_tier, blastup_balance=balances_by_chain_id)


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
