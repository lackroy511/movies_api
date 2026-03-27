import json
from dataclasses import asdict, is_dataclass
from typing import Any, Protocol, TypeVar

import redis.asyncio as aioredis

from src_api.core.config.settings import settings

pool = aioredis.ConnectionPool.from_url(settings.redis_base_url, max_connections=10)
client = aioredis.Redis(connection_pool=pool)

T = TypeVar("T")


class DataclassType(Protocol):
    __dataclass_fields__: dict


class SaveRedisCacheError(Exception):
    pass


class RedisCacheClient:
    OBJ_NOT_DATACLASS_MSG = "Object must be a dataclass"
    
    def __init__(self, client: aioredis.Redis, ttl: int) -> None:
        self.client = client
        self.ttl = settings.redis_cache_ttl

    async def set_cache(self, key: str, dto_obj: DataclassType) -> None:
        if not is_dataclass(dto_obj):
            raise ValueError(self.OBJ_NOT_DATACLASS_MSG)
        
        data = asdict(dto_obj)
        str_data = json.dumps(data)
        is_saved = await self.client.set(key, str_data, ex=self.ttl)
        if not is_saved:
            raise SaveRedisCacheError("Failed to save movie to cache")

    async def get_cache(self, key: str, result_dto_class: type[T]) -> T | None:
        if not is_dataclass(result_dto_class):
            raise ValueError(self.OBJ_NOT_DATACLASS_MSG)
        
        raw_data = await self.client.get(key)
        if not raw_data:
            return None

        json_str = raw_data.decode("utf-8")
        data = json.loads(json_str)
        return result_dto_class(**data)

    async def delete_cache(self, key: str) -> int:
        return await self.client.delete(key)
    
    def build_cache_key(self, prefix: str, *key_args: Any) -> str:  # noqa: ANN401
        key = ":".join(map(str, key_args))
        return f"{prefix}:{key}"


def get_redis_client() -> RedisCacheClient:
    return RedisCacheClient(client, settings.redis_cache_ttl)
