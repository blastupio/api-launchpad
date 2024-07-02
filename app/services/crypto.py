import asyncio

from web3 import Web3
from web3.contract import AsyncContract
from web3.types import TxData, TxReceipt

from app import chains
from app.abi import (
    PRESALE_ABI,
    PRESALE_BSC_ABI,
    PRICE_FEED_ABI,
    PRESALE_BLAST_ABI,
    BLP_STAKING_ORACLE_ABI,
    BLP_BALANCE_ABI,
)
from app.base import logger
from app.services.launchpad.abi import AMOUNT_AND_USD_ABI
from app.services.web3_nodes import web3_node, catch_web3_exceptions


class Crypto:
    def __init__(
        self,
        environment: str,
        contracts: dict[str, str],
        staking_oracle_contract: str,
        blp_balance_contract: str,
        locked_blp_balance_contract: str,
    ):
        self.environment = environment
        self.contracts = contracts
        self.staking_oracle_contract = staking_oracle_contract
        self.blp_balance_contract = blp_balance_contract
        self.locked_blp_balance_contract = locked_blp_balance_contract

    @staticmethod
    def get_network_by_chain_id(chain_id: int) -> str | None:
        _network_by_chain_id = {
            chains.ethereum.id: "eth",
            chains.ethereum_sepolia.id: "eth",
            chains.bsc.id: "bsc",
            chains.bsc_testnet.id: "bsc",
            chains.polygon.id: "polygon",
            chains.polygon_mumbai.id: "polygon",
            chains.blast.id: "blast",
            chains.blast_sepolia.id: "blast",
        }
        return _network_by_chain_id.get(chain_id)

    @catch_web3_exceptions
    async def get_transaction_data(self, network: str, tx_hash: str):
        if self.contracts.get(network) is None:
            return None
        web3 = await web3_node.get_web3(network)
        return await web3.eth.get_transaction(tx_hash)

    @catch_web3_exceptions
    async def get_txn_data(self, chain_id: int, tx_hash: str) -> TxData:
        web3 = await web3_node.get_web3(chain_id=chain_id)
        return await web3.eth.get_transaction(tx_hash)

    @catch_web3_exceptions
    async def get_txn_receipt(self, chain_id: int, tx_hash: str) -> TxReceipt:
        web3 = await web3_node.get_web3(chain_id=chain_id)
        return await web3.eth.get_transaction_receipt(tx_hash)

    @catch_web3_exceptions
    async def wait_for_txn_receipt(
        self, chain_id: int, tx_hash: str, timeout: int = 10, poll_latency: float = 0.5
    ) -> TxReceipt:
        web3 = await web3_node.get_web3(chain_id=chain_id)
        return await web3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=timeout, poll_latency=poll_latency
        )

    @catch_web3_exceptions
    async def get_blastup_token_balance(self, network: str, address: str) -> int:
        if self.contracts.get(network) is None:
            logger.warning(f"get_blastup_token_balance: no contract for {network}")
            return 0

        contract = await self.presale_contract(network)
        address = Web3.to_checksum_address(address)
        tasks = [contract.functions.balances(address).call()] + [
            c.functions.balances(address).call() for c in await self._legacy_contracts(network)
        ]
        res = await asyncio.gather(*tasks, return_exceptions=True)
        balance = sum(x for x in res if x and isinstance(x, int))
        return balance

    @catch_web3_exceptions
    async def get_blp_balance(self, address: str) -> int:
        web3 = await web3_node.get_web3("blast")
        balance_contract_address = web3.to_checksum_address(self.blp_balance_contract)
        balance_contract = web3.eth.contract(balance_contract_address, abi=BLP_BALANCE_ABI)
        locked_balance_contract_address = web3.to_checksum_address(self.locked_blp_balance_contract)
        locked_balance_contract = web3.eth.contract(
            locked_balance_contract_address, abi=BLP_BALANCE_ABI
        )

        address = Web3.to_checksum_address(address)
        tasks = [
            balance_contract.functions.balanceOf(address).call(),
            locked_balance_contract.functions.balanceOf(address).call(),
        ]
        res = await asyncio.gather(*tasks, return_exceptions=True)
        balance = sum(x for x in res if x and isinstance(x, int))
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

        contract = await self.presale_contract(network)
        price_feed_addr = await contract.functions.COIN_PRICE_FEED().call()

        web3 = await web3_node.get_web3(network)
        price_feed_contract = web3.eth.contract(
            web3.to_checksum_address(price_feed_addr), abi=PRICE_FEED_ABI
        )
        return {
            "latestAnswer": await price_feed_contract.functions.latestAnswer().call(),
            "decimals": int(await price_feed_contract.functions.decimals().call()),
        }

    @catch_web3_exceptions
    async def get_blp_staking_value(self, wallet_address: str) -> int:
        web3 = await web3_node.get_web3(network="blast")  # todo: change to chain_id
        wallet_address = web3.to_checksum_address(wallet_address)
        contract_address = web3.to_checksum_address(self.staking_oracle_contract)
        contract = web3.eth.contract(contract_address, abi=BLP_STAKING_ORACLE_ABI)
        res = int(await contract.functions.balanceOf(wallet_address).call())
        return res

    async def presale_contract(self, network, contract_address: str | None = None) -> AsyncContract:
        abi = {
            "eth": PRESALE_ABI,
            "polygon": PRESALE_ABI,
            "bsc": PRESALE_BSC_ABI,
            "blast": PRESALE_BLAST_ABI,
            "base": PRESALE_ABI,
        }[network]
        web3 = await web3_node.get_web3(network)
        if contract_address:
            address = web3.to_checksum_address(contract_address)
        else:
            address = web3.to_checksum_address(self.contracts[network])
        return web3.eth.contract(address, abi=abi)

    async def amount_and_usd_contract(self, network: str, address: str) -> AsyncContract:
        web3 = await web3_node.get_web3(network)
        address = web3.to_checksum_address(address)
        return web3.eth.contract(address, abi=AMOUNT_AND_USD_ABI)

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
