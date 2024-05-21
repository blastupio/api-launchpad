import asyncio

from app.dependencies import get_launchpad_crypto
from app.schema import ChainId
from app.services.balances.redis import blastup_balance_redis
from app import chains


async def get_blastup_tokens_balance_for_chains(address: str) -> dict[ChainId, int]:
    _chain_to_chain_id = {
        "eth": chains.ethereum.id,
        "bsc": chains.bsc.id,
        "polygon": chains.polygon.id,
        "blast": chains.blast.id,
        "base": chains.base.id,
    }
    _chain_id_to_chain = {_chain_to_chain_id[chain]: chain for chain in _chain_to_chain_id}

    balance_in_cache = await blastup_balance_redis.get(
        address=address, chain_ids=_chain_to_chain_id.values()
    )
    if len(balance_in_cache) == len(_chain_to_chain_id):
        # balances for all chains are in cache
        return balance_in_cache

    crypto = get_launchpad_crypto()
    chain_ids_via_blockchain = list(
        set(_chain_to_chain_id.values()).difference(set(balance_in_cache.keys()))
    )
    tasks = [
        crypto.get_blastup_token_balance(network=_chain_id_to_chain[chain_id], address=address)
        for chain_id in chain_ids_via_blockchain
    ]
    balances = await asyncio.gather(*tasks)
    res = dict(zip(chain_ids_via_blockchain, balances))
    res.update(balance_in_cache)
    if res:
        await blastup_balance_redis.set(address, res)
    return res
