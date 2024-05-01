import asyncio

from web3 import AsyncWeb3, AsyncHTTPProvider

from app.base import logger
from app.env import settings
from app.services.stake_history.abi import staking_abi
from app.services.stake_history.redis_cli import stake_history_redis


async def monitor_staking_contract():
    web3 = AsyncWeb3(AsyncHTTPProvider(settings.crypto_api_key_blast))
    chain_id = await web3.eth.chain_id
    current_block = await web3.eth.block_number
    last_checked_block = await stake_history_redis.get_last_checked_block(chain_id)
    if last_checked_block is None:
        last_checked_block = current_block - 4999
        logger.info(
            f"No last checked block found for chain {chain_id}, setting to {last_checked_block}"
        )

    if last_checked_block >= current_block:
        return

    staking_contract = web3.eth.contract(
        address=web3.to_checksum_address(settings.yield_staking_contract_addr),
        abi=staking_abi,
    )
    while True:
        from_block = last_checked_block + 1
        to_block = min(current_block, from_block + 4999)
        logger.info(f"Monitoring from block {from_block} to block {to_block}")

        if from_block > to_block:
            logger.info(f"No events from block {from_block} to block {to_block}")
            break

        events = await staking_contract.events.Staked().get_logs(
            fromBlock=from_block, toBlock=to_block
        )
        for event in events:
            logger.info(f"stake {event.args}")

        events = await staking_contract.events.Withdrawn().get_logs(
            fromBlock=from_block, toBlock=to_block
        )
        for event in events:
            logger.info(f"withdraw {event.args}")

        last_checked_block = to_block
        await stake_history_redis.set_last_checked_block(chain_id, to_block)


asyncio.run(monitor_staking_contract())
