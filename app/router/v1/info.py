from fastapi import APIRouter, Path, Query
from web3 import Web3

from app.base import logger
from app.consts import NATIVE_TOKEN_ADDRESS
from app.dependencies import RedisDep, CryptoDep
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
)
from app.services.tiers.consts import (
    bronze_tier,
    silver_tier,
    gold_tier,
    titanium_tier,
    platinum_tier,
    diamond_tier,
)
from app.services.tiers.user_tier import get_user_tier
from app.utils import get_data_with_cache
from app.services.prices import get_tokens_price, get_any2any_prices

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
    redis: RedisDep,
    crypto: CryptoDep,
    address: str = Path(
        pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"
    ),
):
    try:
        polygon = await get_data_with_cache(
            f"address-balance:polygon:{address}",
            lambda: crypto.get_token_balance("polygon", address),
            redis,
        )
        eth = await get_data_with_cache(
            f"address-balance:eth:{address}",
            lambda: crypto.get_token_balance("eth", address),
            redis,
        )
        bsc = await get_data_with_cache(
            f"address-balance:bsc:{address}",
            lambda: crypto.get_token_balance("bsc", address),
            redis,
        )
        blast = await get_data_with_cache(
            f"address-balance:blast:{address}",
            lambda: crypto.get_token_balance("blast", address),
            redis,
        )
    except Exception as e:
        logger.error(f"Cannot get balance for {address}: {e}")
        return InternalServerError("Failed to get user info")
    else:
        blastup_balance_by_chain_id = {
            ChainId(1): eth,
            ChainId(56): bsc,
            ChainId(137): polygon,
            ChainId(81457): blast,
        }
        user_tier = get_user_tier(blastup_balance_by_chain_id)
        return UserInfoResponse(tier=user_tier, blastup_balance=blastup_balance_by_chain_id)


@router.get("/tiers", response_model=TierInfoResponse)
async def get_all_tiers():
    return {
        "tiers": [bronze_tier, silver_tier, gold_tier, titanium_tier, platinum_tier, diamond_tier]
    }
