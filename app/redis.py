from redis.asyncio import from_url, Redis

from app.env import settings

redis_cli: Redis = from_url(str(settings.redis_url))
