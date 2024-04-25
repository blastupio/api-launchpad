from redis.asyncio import from_url, Redis

from app.env import REDIS_URL

redis_cli: Redis = from_url(REDIS_URL)
