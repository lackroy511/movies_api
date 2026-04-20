import json
from abc import ABC, abstractmethod
from typing import Any

import redis.asyncio as aioredis
from redis.exceptions import ConnectionError, TimeoutError

from src_auth.core.config.settings import settings
from src_auth.core.db.exceptions import SaveRedisCacheError
from src_auth.utils.backoff import Backoff

pool = aioredis.ConnectionPool.from_url(settings.redis_base_url, max_connections=10)
client = aioredis.Redis(connection_pool=pool)


class CacheClientInterface(ABC):
    @abstractmethod
    async def set_cache(self, key: str, data: dict[str, Any], ttl: int) -> None: ...

    @abstractmethod
    async def get_cache(self, key: str) -> dict[str, Any] | None: ...

    @abstractmethod
    async def delete_cache(self, key: str) -> int: ...

    @abstractmethod
    def build_cache_key(self, prefix: str, *key_args: Any) -> str:  # noqa: ANN401
        pass

    @abstractmethod
    async def scan_keys(self, pattern: str) -> list[str]: ...


RETRY_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
)


class RedisCacheClient(CacheClientInterface):
    def __init__(self, client: aioredis.Redis) -> None:
        self.client = client

    @Backoff(RETRY_EXCEPTIONS)
    async def set_cache(self, key: str, data: dict[str, Any], ttl: int) -> None:
        str_data = json.dumps(data)
        is_saved = await self.client.set(key, str_data, ex=ttl)
        if not is_saved:
            raise SaveRedisCacheError("Failed to save movie to cache")

    @Backoff(RETRY_EXCEPTIONS)
    async def get_cache(self, key: str) -> dict[str, Any] | None:
        raw_data = await self.client.get(key)
        if not raw_data:
            return None

        json_str = raw_data.decode("utf-8")
        return json.loads(json_str)

    @Backoff(RETRY_EXCEPTIONS)
    async def delete_cache(self, key: str) -> int:
        return await self.client.delete(key)

    @Backoff(RETRY_EXCEPTIONS)
    async def scan_keys(self, pattern: str) -> list[str]:
        keys = []
        cursor = 0
        while True:
            cursor, keys_batch = await self.client.scan(
                cursor=cursor,
                match=pattern,
                count=100,
            )
            keys.extend(keys_batch)
            if cursor == 0:
                break
        return keys
    
    def build_cache_key(self, prefix: str, *key_args: Any) -> str:  # noqa: ANN401
        key = ":".join(map(str, key_args))
        return f"{prefix}:{key}"


def get_redis_client() -> CacheClientInterface:
    return RedisCacheClient(client)
