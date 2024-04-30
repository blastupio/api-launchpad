import asyncio

from typing import Any

from eth_account import Account
from eth_account.hdaccount import seed_from_mnemonic, key_from_seed
from web3 import Web3
from web3.contract import AsyncContract
from web3.contract.base_contract import BaseContractFunction

from app.abi import (
    ERC20_ABI,
    PRESALE_ABI,
    PRESALE_BSC_ABI,
    PRICE_FEED_ABI,
    PRESALE_BLAST_ABI,
)
from app.services.web3_nodes import web3_node, catch_web3_exceptions


class Crypto:
    def __init__(
        self,
        environment: str,
        contracts: dict[str, str],
        usdt_contracts: dict[str, str],
        private_key_seed: str,
        onramp_private_key_seed: str,
    ):
        self.environment = environment
        self.contracts = contracts
        self.usdt_contracts = usdt_contracts

        seed = seed_from_mnemonic(private_key_seed, passphrase="")
        private_key = key_from_seed(seed, account_path="m/44'/60'/0'/0/{}".format(0))
        self.private_key = private_key
        self.address = Account.from_key(private_key).address

        seed = seed_from_mnemonic(onramp_private_key_seed, passphrase="")
        private_key = key_from_seed(seed, account_path="m/44'/60'/0'/0/{}".format(0))
        self.onramp_private_key = private_key
        self.onramp_address = Account.from_key(private_key).address

        self.stages = [
            2500000,
            5000000,
            11250000,
            38750000,
            76250000,
            117500000,
            155000000,
            190000000,
            197500000,
            200000000,
        ]
        self.stage_diff = [
            2500000,
            2500000,
            6250000,
            27500000,
            37500000,
            41250000,
            37500000,
            35000000,
            7500000,
            2500000,
        ]
        self.stage_prices = [
            0.02,
            0.03,
            0.04,
            0.05,
            0.055,
            0.06,
            0.065,
            0.07,
            0.08,
            0.09,
        ]

    @catch_web3_exceptions
    async def change_stage(self, network: str, new_stage: int):
        if self.contracts.get(network) is None:
            return None

        web3 = await web3_node.get_web3(network)
        contract = await self._contract(network)
        address = web3.to_checksum_address(self.address)
        nonce = await web3.eth.get_transaction_count(address, block_identifier="latest")

        gas = await contract.functions.setStage(new_stage).estimate_gas({"from": address})
        gas = int(gas * 1.5)

        transaction = await contract.functions.setStage(new_stage).build_transaction(
            {
                "gas": gas,
                "nonce": nonce,
                "gasPrice": await web3.eth.gas_price,
                "chainId": await web3.eth.chain_id,
            }
        )
        signed_tx = web3.eth.account.sign_transaction(transaction, self.private_key)
        return (await web3.eth.send_raw_transaction(signed_tx.rawTransaction)).hex()

    @catch_web3_exceptions
    async def change_usdt_allowance(self, network: str) -> str | None:
        if self.usdt_contracts.get(network) is None:
            return None

        web3 = await web3_node.get_web3(network)
        contract = web3.eth.contract(
            address=web3.to_checksum_address(self.usdt_contracts[network]),
            abi=ERC20_ABI,
        )

        nonce = await web3.eth.get_transaction_count(
            web3.to_checksum_address(self.onramp_address), block_identifier="latest"
        )
        gas = await contract.functions.approve(
            web3.to_checksum_address(self.contracts[network]),
            115792089237316195423570985008687907853269984665640564039457584007913129639935,
        ).estimate_gas({"from": web3.to_checksum_address(self.onramp_address)})
        gas = int(gas * 1.5)

        transaction = await contract.functions.approve(
            web3.to_checksum_address(self.contracts[network]),
            115792089237316195423570985008687907853269984665640564039457584007913129639935,
        ).build_transaction(
            {
                "gas": gas,
                "nonce": nonce,
                "gasPrice": await web3.eth.gas_price,
                "chainId": await web3.eth.chain_id,
            }
        )
        signed_tx = web3.eth.account.sign_transaction(transaction, self.onramp_private_key)
        return (await web3.eth.send_raw_transaction(signed_tx.rawTransaction)).hex()

    @catch_web3_exceptions
    async def mint_tokens_to_address(
        self, network: str, address: str, amount: str
    ) -> tuple[str, int] | None:
        if self.contracts.get(network) is None:
            return None

        contract = await self._contract(network)
        web3 = await web3_node.get_web3(network)

        nonce = await web3.eth.get_transaction_count(
            web3.to_checksum_address(self.onramp_address),
            block_identifier="latest",
        )
        gas = await contract.functions.depositUSDTTo(
            web3.to_checksum_address(address),
            int(float(amount) * 1e6),
            web3.to_checksum_address(address),
        ).estimate_gas(
            {
                "from": web3.to_checksum_address(self.onramp_address),
            }
        )
        gas = int(gas * 1.5)

        transaction = await contract.functions.depositUSDTTo(
            web3.to_checksum_address(address),
            int(float(amount) * 1e6),
            web3.to_checksum_address(address),
        ).build_transaction(
            {
                "gas": gas,
                "nonce": nonce,
                "gasPrice": await web3.eth.gas_price,
                "chainId": await web3.eth.chain_id,
            }
        )
        signed_tx = web3.eth.account.sign_transaction(transaction, self.onramp_private_key)
        return (await web3.eth.send_raw_transaction(signed_tx.rawTransaction)).hex(), nonce

    @catch_web3_exceptions
    async def get_usdt_allowance(self, network: str) -> int:
        if self.usdt_contracts.get(network) is None:
            return 0

        web3 = await web3_node.get_web3(network)
        contract = web3.eth.contract(
            address=web3.to_checksum_address(self.usdt_contracts[network]),
            abi=ERC20_ABI,
        )
        return await contract.functions.allowance(
            web3.to_checksum_address(self.address), self.contracts[network]
        ).call()

    @catch_web3_exceptions
    async def get_transaction_data(self, network: str, tx_hash: str):
        if self.contracts.get(network) is None:
            return None
        web3 = await web3_node.get_web3(network)
        return await web3.eth.get_transaction(tx_hash)

    @catch_web3_exceptions
    async def get_transaction_receipt(self, network: str, tx_hash: str):
        if self.contracts.get(network) is None:
            return None
        web3 = await web3_node.get_web3(network)
        return await web3.eth.get_transaction_receipt(tx_hash)

    @catch_web3_exceptions
    async def get_blastup_token_balance(self, network: str, address: str) -> int:
        if self.contracts.get(network) is None:
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
    async def get_contract_stage(self, network: str) -> int:
        if self.contracts.get(network) is None:
            return 0

        contract = await self._contract(network)
        return int(await contract.functions.stageIterator().call())

    @catch_web3_exceptions
    async def get_total_tokens_sold_usd_agg(self) -> float:
        polygon = await self.get_total_tokens_sold_usd("polygon")
        eth = await self.get_total_tokens_sold_usd("eth")
        bsc = await self.get_total_tokens_sold_usd("bsc")
        blast = await self.get_total_tokens_sold_usd("blast")

        return polygon + eth + bsc + blast

    @catch_web3_exceptions
    async def get_total_tokens_sold_agg(self) -> int:
        polygon = await self.get_total_tokens_sold("polygon")
        eth = await self.get_total_tokens_sold("eth")
        bsc = await self.get_total_tokens_sold("bsc")
        blast = await self.get_total_tokens_sold("blast")

        return polygon + eth + bsc + blast

    @catch_web3_exceptions
    async def get_total_tokens_sold_usd(self, network: str) -> float:
        if self.contracts.get(network) is None:
            return 0

        contract = await self._contract(network)
        total_usd = int(await contract.functions.totalSoldInUSD().call())
        for c in await self._legacy_contracts(network):
            total_usd += int(await c.functions.totalSoldInUSD().call())

        return total_usd / 1e8

    @catch_web3_exceptions
    async def get_total_tokens_sold(self, network: str) -> int:
        if self.contracts.get(network) is None:
            return 0

        contract = await self._contract(network)
        total = int(await contract.functions.totalTokensSold().call())
        for c in await self._legacy_contracts(network):
            total += int(await c.functions.totalTokensSold().call())

        return total

    @catch_web3_exceptions
    async def get_price_feed(self, token) -> dict[str, float | int]:
        if token.lower() not in ["eth", "matic", "bnb", "weth"]:
            return {}

        network = {"eth": "eth", "matic": "polygon", "bnb": "bsc", "weth": "blast"}[token.lower()]
        if self.usdt_contracts.get(network) is None:
            return {}

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

    async def parse_input(
        self, network: str, i: str
    ) -> tuple["BaseContractFunction", dict[str, Any]]:
        contract = await self._contract(network)
        return contract.decode_function_input(i)

    async def _contract(self, network) -> AsyncContract:
        abi = {
            "eth": PRESALE_ABI,
            "polygon": PRESALE_ABI,
            "bsc": PRESALE_BSC_ABI,
            "blast": PRESALE_BLAST_ABI,
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
        }
        return contracts.get(network)
