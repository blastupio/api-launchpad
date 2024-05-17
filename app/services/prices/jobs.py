import asyncio
from typing import Any

from fastapi import Depends

from app.base import logger
from app.common import Command, CommandResult
from app.crud.supported_tokens import SupportedTokensCrud
from app.dependencies import get_supported_tokens_crud
from app.schema import ChainId
from app.services.coingecko.client import coingecko_cli
from app.services.prices.cache import token_price_cache


class UpdateSupportedTokensCache(Command):
    async def command(
        self,
        crud: SupportedTokensCrud = Depends(get_supported_tokens_crud),
    ) -> CommandResult:
        rows = await crud.get_supported_tokens()
        logger.info(f"TokenPriceCache: {len(rows)} rows")

        token_addresses_by_chain_id = {}
        for row in rows:
            token_addresses_by_chain_id.setdefault(row.chain_id, []).append(row.token_address)

        tasks = []
        for chain_id, token_addresses in token_addresses_by_chain_id.items():
            tasks.append(coingecko_cli.get_tokens_price(chain_id, token_addresses))
        prices_result = await asyncio.gather(*tasks)

        prices_agg: dict[ChainId, dict[str, Any]] = {}
        for chain_id, prices in zip(token_addresses_by_chain_id.keys(), prices_result):
            prices_agg[chain_id] = prices

        await token_price_cache.set(prices_agg)
        return CommandResult(success=True)
