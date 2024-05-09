import contextvars
import functools
import json
import traceback
from datetime import timedelta

from redis.asyncio import Redis, from_url
from web3 import AsyncWeb3, AsyncHTTPProvider, exceptions

from app.env import settings
from app.schema import ChainId
from app.base import logger
from app import chains


chain_id_ctx = contextvars.ContextVar("chain_id")

ERROR_COUNTS_TO_SWITCH_TO_FALLBACK = 5


def catch_web3_exceptions(func):
    """
    If a Web3 exception is caught, the error is logged and the error count is incremented.
    If the error count exceeds a certain threshold, the fallback node URL is set.
    """

    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except exceptions.Web3Exception as e:
            # todo: catch more specific errors, not just Web3Exception
            logger.error(f"Caught web3 error: {e}\n\n{traceback.format_exc()}")
            if chain_id := chain_id_ctx.get():
                # Increment the error count for this chain_id
                err_counts = await web3_node_redis.increment_web3_errors_count(chain_id)
                logger.info(f"Error count for {chain_id=}: {err_counts}")
                if (
                    err_counts > ERROR_COUNTS_TO_SWITCH_TO_FALLBACK
                    and not await web3_node_redis.fallback_url_exists(chain_id)
                ):
                    # Exceed number of error and no fallback => set the fallback node URL
                    fallback_url = web3_node.get_fallback_node_url(chain_id)
                    logger.info(f"Setting fallback URL for {chain_id=}")
                    await web3_node_redis.set_fallback_node_url(chain_id=chain_id, url=fallback_url)
            raise e

    return wrapper


class Web3NodeRedis:
    __FALLBACK_NODE_MINUTES = 5
    __WEB3_ERRORS_INTERVAL_MINUTES = 1

    def __init__(self):
        self._redis: Redis | None = None

    @property
    def redis(self) -> Redis:
        if not self._redis:
            self._redis = from_url(str(settings.redis_url))
        return self._redis

    async def get_fallback_node_url(self, chain_id: ChainId) -> str | None:
        key = f"fallback_node_url_{chain_id}"
        _url = await self.redis.get(key)
        url = json.loads(_url) if _url else None
        return url

    async def set_fallback_node_url(self, chain_id: ChainId, url: str) -> None:
        key = f"fallback_node_url_{chain_id}"
        await self.redis.setex(
            key,
            value=json.dumps(url),
            time=timedelta(minutes=self.__FALLBACK_NODE_MINUTES),
        )

    async def fallback_url_exists(self, chain_id: ChainId) -> bool:
        key = f"fallback_node_url_{chain_id}"
        return await self.redis.exists(key)

    async def get_web3_errors_count(self, chain_id: ChainId) -> int:
        key = f"web3_errors_count_{chain_id}"
        count = await self.redis.get(key)
        return int(count) if count else 0

    async def increment_web3_errors_count(self, chain_id: ChainId) -> int:
        key = f"web3_errors_count_{chain_id}"
        exist_count = await self.redis.get(key)
        if exist_count:
            count = json.loads(exist_count) + 1
            await self.redis.set(key, count)
        else:
            count = 1
            await self.redis.setex(
                key,
                value=json.dumps(count),
                time=timedelta(minutes=self.__WEB3_ERRORS_INTERVAL_MINUTES),
            )
        return count


class Web3Node:
    _network_to_chain_id: dict[str, ChainId] = {
        "eth": chains.ethereum.id,
        "polygon": chains.polygon.id,
        "bsc": chains.bsc.id,
        "blast": chains.blast.id,
    }

    def __init__(self, redis: Web3NodeRedis):
        self.node_redis = redis
        self._web3_by_chain_id = {
            chains.polygon.id: AsyncWeb3(AsyncHTTPProvider(settings.crypto_api_key_polygon)),
            chains.ethereum.id: AsyncWeb3(AsyncHTTPProvider(settings.crypto_api_key_eth)),
            chains.bsc.id: AsyncWeb3(AsyncHTTPProvider(settings.crypto_api_key_bsc)),
            chains.blast.id: AsyncWeb3(AsyncHTTPProvider(settings.crypto_api_key_blast)),
        }
        self._fallback_node_urls_by_chain_id = {
            chains.polygon.id: settings.fallback_api_url_polygon,
            chains.ethereum.id: settings.fallback_api_url_eth,
            chains.bsc.id: settings.fallback_api_url_bsc,
            chains.blast.id: settings.fallback_api_url_blast,
        }
        self._fallback_api_key_by_chain_id = {
            chains.polygon.id: settings.fallback_api_key_polygon,
            chains.ethereum.id: settings.fallback_api_key_eth,
            chains.bsc.id: settings.fallback_api_key_eth,
            chains.blast.id: settings.fallback_api_key_blast,
        }
        assert (
            self._web3_by_chain_id.keys() == self._fallback_node_urls_by_chain_id.keys()
        ), "Not all networks have fallback nodes"

    def _get_chain_id(self, network: str) -> ChainId:
        return self._network_to_chain_id[network]

    def get_fallback_node_url(self, chain_id: ChainId) -> str:
        return self._fallback_node_urls_by_chain_id[chain_id]

    def get_fallback_api_key(self, chain_id: ChainId) -> str | None:
        return self._fallback_api_key_by_chain_id.get(chain_id)

    async def get_web3(
        self, network: str | None = None, chain_id: ChainId | None = None
    ) -> AsyncWeb3:
        """
        If there is fallback node in redis, use it.
        Otherwise, use the default node
        """
        # todo: use chain_id instead of network
        assert not all((network, chain_id)), "network and chain_id are mutually exclusive"
        assert any((network, chain_id)), "at least one network or chain_id must be provided"
        if network:
            chain_id = self._get_chain_id(network)
        chain_id_ctx.set(chain_id)

        if url := (await self.node_redis.get_fallback_node_url(chain_id)):
            options = {}
            if fallback_api_key := self.get_fallback_api_key(chain_id):
                options = {
                    "headers": {
                        "x-api-key": fallback_api_key,
                        "Content-Type": "application/json",
                    }
                }

            logger.info(f"Using fallback node for {chain_id=}, {url=}")
            return AsyncWeb3(AsyncHTTPProvider(url, request_kwargs=options))
        return self._web3_by_chain_id[chain_id]


web3_node_redis = Web3NodeRedis()
web3_node = Web3Node(redis=web3_node_redis)
