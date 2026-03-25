import redis.asyncio as aioredis

from src_api.core.config.settings import settings

pool = aioredis.ConnectionPool.from_url(settings.redis_base_url, max_connections=10)
client = aioredis.Redis(connection_pool=pool)


def get_redis_client() -> aioredis.Redis:
    return client