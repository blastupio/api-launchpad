import hashlib
import hmac
import statistics
from collections import OrderedDict
from urllib.parse import urlencode
from uuid import UUID

from eth_account import Account
from eth_account.hdaccount import seed_from_mnemonic, key_from_seed
from httpx import AsyncClient
from web3 import AsyncWeb3, AsyncHTTPProvider, Web3

from app.base import logger


class Crypto:
    def __init__(self, api_key: str, sender_seed_phrase: str):
        self.web3 = AsyncWeb3(AsyncHTTPProvider(api_key))

        seed = seed_from_mnemonic(sender_seed_phrase, passphrase="")
        self.private_key = key_from_seed(seed, account_path="m/44'/60'/0'/0/0")
        self.address = Account.from_key(self.private_key).address

    async def send_eth(self, recipient: str, amount: str) -> str | None:
        async def estimate_gas() -> int:
            block = await self.web3.eth.get_block("latest", full_transactions=True)
            median_gas = int(statistics.median(t.gas for t in block.transactions))
            return median_gas

        nonce = self.web3.eth.get_transaction_count(self.web3.to_checksum_address(self.address), "latest")
        gas = await estimate_gas()
        gas_price = max(await self.web3.eth.gas_price, Web3.to_wei(30, "gwei"))

        transaction = {
            "chainId": await self.web3.eth.chain_id,
            "gas": int(gas * 1.2),
            "gasPrice": gas_price,
            "nonce": nonce,
            "from": self.web3.to_checksum_address(self.address),
            "to": self.web3.to_checksum_address(recipient),
            "value": int(amount),
        }

        signed_tx = self.web3.eth.account.sign_transaction(transaction, self.private_key)
        tx_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash.hex()


class Munzen:
    PRODUCTION_BASE_URL = "https://widget.munzen.io/"
    STAGE_BASE_URL = "https://stage-widget.munzen.io/"

    PRODUCTION_API_URL = "https://widget-backend.prod.gcp.munzen.io/"
    STAGE_API_URL = "https://widget-backend.sandbox.gcp.munzen.io/"

    def __init__(self, api_key: str, secret_key: str, environment: str, onramp_wallet: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.environment = environment
        self.onramp_wallet = onramp_wallet

    async def calculate_signature(self, payload: dict) -> str:
        signature_payload = payload.copy()
        if "apiKey" in signature_payload:
            del signature_payload["apiKey"]
        sorted_payload = self._sort_payload(signature_payload)
        payload_as_str = self._to_str(sorted_payload)

        return hmac.new(
            key=self.secret_key.encode("utf-8"),
            msg=payload_as_str.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

    async def generate_link(self, merchant_order_id: str | UUID, amount: str, currency: str) -> str:
        query_params = {
            "toWallet": self.onramp_wallet,
            "toCurrency": currency,
            "toAmount": amount,
            "fromCurrency": "USD",
            "merchantOrderId": str(merchant_order_id),
            "apiKey": self.api_key,
        }
        query_params["signature"] = await self.calculate_signature(query_params)

        return f"{self.base_url}?{urlencode(query_params)}"

    async def get_order_data(self, munzen_order_id: str) -> dict:
        async with AsyncClient() as client:
            input_data = {
                "signature": await self.calculate_signature({"orderId": munzen_order_id}),
                "apiKey": self.api_key,
                "payload[orderId]": munzen_order_id,
            }

            response = await client.get(
                f"{self.api_url}api/v1/merchants/orders/{munzen_order_id}?{urlencode(input_data)}")
            if response.status_code != 200:
                raise Exception(f"API Error. Status code: {response.status_code}")

            json_response = response.json()
        return json_response

    async def validate_webhook(self, payload: dict, signature: str) -> bool:
        computed_signature = await self.calculate_signature(payload)

        if computed_signature != signature:
            logger.debug(
                "[Munzen.webhook] Invalid signature",
                extra={
                    "payload": payload,
                    "computed_signature": computed_signature,
                    "webhook_signature": signature,
                },
            )
            return False
        return True

    @property
    def base_url(self) -> str:
        return self.PRODUCTION_BASE_URL if self.environment[:4] == "prod" else self.STAGE_BASE_URL

    @property
    def api_url(self) -> str:
        return self.PRODUCTION_API_URL if self.environment[:4] == "prod" else self.STAGE_API_URL

    def _sort_payload(self, payload: dict) -> OrderedDict:
        result = OrderedDict(sorted(payload.items()))
        for k, v in result.items():
            if type(v) is dict:
                result[k] = self._sort_payload(v)
        return result

    def _to_str(self, payload: OrderedDict) -> str:
        result = ""
        for k, v in payload.items():
            if not (type(v) is dict or type(v) is OrderedDict):
                result += f"{k}:{v}" if v is not None else f"{k}:"
            else:
                result += f"{k}:{self._to_str(v)}"

        return result
