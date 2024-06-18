import asyncio

from redis.asyncio import Redis

from app.dependencies import get_redis

BLASTUP_BALANCE_TTL_SECONDS = 30


class BlastupBalanceRedis:
    def __init__(self, redis_cli: Redis):
        self.__redis_cli = redis_cli

    @property
    def redis(self):
        return self.__redis_cli

    @staticmethod
    def __get_key(chain_id: int, address: str) -> str:
        return f"blastup_token_balance_{address.lower()}_{chain_id}"

    @staticmethod
    def __get_chain_id_from_key(key: str) -> int:
        return int(key.split("_")[-1])

    async def set(self, address: str, balance_by_chain_id: dict[int, int]) -> None:  # noqa
        tasks = []
        for chain_id, balance in balance_by_chain_id.items():
            tasks.append(
                self.redis.set(
                    self.__get_key(chain_id, address),
                    value=str(balance),
                    ex=BLASTUP_BALANCE_TTL_SECONDS,
                )
            )
        await asyncio.gather(*tasks)

    async def get(self, address: str, chain_ids: list[int]) -> dict[int, int]:
        keys = [self.__get_key(chain_id, address) for chain_id in chain_ids]
        data = await self.redis.mget(keys)
        res = {
            self.__get_chain_id_from_key(key): int(value) for key, value in zip(keys, data) if value
        }
        return res


blastup_balance_redis = BlastupBalanceRedis(redis_cli=get_redis())


class BLPBalanceRedis:
    def __init__(self, redis_cli: Redis):
        self.__redis_cli = redis_cli

    @property
    def redis(self):
        return self.__redis_cli

    @staticmethod
    def __get_key(address: str) -> str:
        return f"blp_balance_{address.lower()}"

    async def set(self, address: str, balance: int) -> None:  # noqa: A003
        await self.redis.set(
            self.__get_key(address),
            value=str(balance),
            ex=BLASTUP_BALANCE_TTL_SECONDS,
        )

    async def get(self, address: str) -> int:
        data = await self.redis.get(self.__get_key(address))
        return int(data) if data is not None else None


blp_balance_redis = BLPBalanceRedis(redis_cli=get_redis())
