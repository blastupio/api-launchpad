import asyncio

from web3 import Web3
from web3.contract import AsyncContract

from app.abi import (
    PRESALE_ABI,
    PRESALE_BSC_ABI,
    PRICE_FEED_ABI,
    PRESALE_BLAST_ABI,
)
from app.base import logger
from app.services.web3_nodes import web3_node, catch_web3_exceptions


class Crypto:
    def __init__(
        self,
        environment: str,
        contracts: dict[str, str],
    ):
        self.environment = environment
        self.contracts = contracts

    @catch_web3_exceptions
    async def get_transaction_data(self, network: str, tx_hash: str):
        if self.contracts.get(network) is None:
            return None
        web3 = await web3_node.get_web3(network)
        return await web3.eth.get_transaction(tx_hash)

    @catch_web3_exceptions
    async def get_blastup_token_balance(self, network: str, address: str) -> int:
        if self.contracts.get(network) is None:
            logger.error(f"get_blastup_token_balance: no contract for {network}")
            return 0

        contract = await self._contract(network)
        address = Web3.to_checksum_address(address)
        tasks = [contract.functions.balances(address).call()] + [
            c.functions.balances(address).call() for c in await self._legacy_contracts(network)
        ]
        res = await asyncio.gather(*tasks, return_exceptions=True)
        balance = sum(int(x) for x in res if x and isinstance(x, int))
        return balance

    @catch_web3_exceptions
    async def get_price_feed(self, token) -> dict[str, float | int]:
        if token.lower() not in ["eth", "matic", "bnb", "weth", "weth_base"]:
            return {}

        network = {
            "eth": "eth",
            "matic": "polygon",
            "bnb": "bsc",
            "weth": "blast",
            "weth_base": "base",
        }[token.lower()]

        contract = await self._contract(network)
        price_feed_addr = await contract.functions.COIN_PRICE_FEED().call()

        web3 = await web3_node.get_web3(network)
        price_feed_contract = web3.eth.contract(
            web3.to_checksum_address(price_feed_addr), abi=PRICE_FEED_ABI
        )
        return {
            "latestAnswer": await price_feed_contract.functions.latestAnswer().call(),
            "decimals": int(await price_feed_contract.functions.decimals().call()),
        }

    async def _contract(self, network) -> AsyncContract:
        abi = {
            "eth": PRESALE_ABI,
            "polygon": PRESALE_ABI,
            "bsc": PRESALE_BSC_ABI,
            "blast": PRESALE_BLAST_ABI,
            "base": PRESALE_ABI,
        }[network]
        web3 = await web3_node.get_web3(network)
        contract_address = web3.to_checksum_address(self.contracts[network])
        return web3.eth.contract(contract_address, abi=abi)

    async def _legacy_contracts(self, network) -> list[AsyncContract]:
        if self.environment == "testnet":
            return []

        web3 = await web3_node.get_web3(network)
        contracts = {
            "eth": [],
            "polygon": [],
            "bsc": [
                web3.eth.contract(
                    web3.to_checksum_address("0x765eE5652281D2a17D4e43AeA97a5D47280079a7"),
                    abi=PRESALE_ABI,
                )
            ],
            "blast": [],
            "base": [],
        }
        return contracts.get(network)
