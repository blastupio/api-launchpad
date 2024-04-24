from fastapi import APIRouter, Path, Query
from web3 import Web3

from app.consts import NATIVE_TOKEN_ADDRESS
from app.schema import (
    TierInfoResponse,
    UserInfoResponse,
    ChainId,
    Address,
    TokenInChain,
    TokenPriceResponse,
    Any2AnyPriceResponse,
)
from app.services.prices import get_tokens_price

router = APIRouter(prefix="/info", tags=["info"])


@router.get("/token-price", response_model=TokenPriceResponse)
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
    return {
        "rate": {
            1: {
                "0x0000000000000000000000000000000000000000": 123.12,
            }
        }
    }


@router.get("/user/{address}", response_model=UserInfoResponse)
async def get_user_info(
    address: str = Path(
        pattern="^(0x)[0-9a-fA-F]{40}$", example="0xE1784da2b8F42C31Fb729E870A4A8064703555c2"
    )
):
    return {}


@router.get("/tiers", response_model=TierInfoResponse)
async def get_all_tiers():
    # todo: remove hardcode
    return {
        "tiers": [
            {
                "order": 1,
                "title": "Bronze",
                "blp_amount": 2000,
            },
            {
                "order": 2,
                "title": "Silver",
                "blp_amount": 5000,
            },
            {
                "order": 3,
                "title": "Gold",
                "blp_amount": 10_000,
            },
            {
                "order": 4,
                "title": "Titanium",
                "blp_amount": 20_000,
            },
            {
                "order": 5,
                "title": "Platinum",
                "blp_amount": 50_000,
            },
            {
                "order": 6,
                "title": "Diamond",
                "blp_amount": 150_000,
            },
        ]
    }
