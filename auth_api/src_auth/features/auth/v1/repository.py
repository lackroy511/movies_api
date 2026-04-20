from src_auth.core.db.cache import CacheClientInterface, get_redis_client
from fastapi import Depends
from typing import Annotated

from src_auth.core.config.settings import settings


class AuthTokenRepoInterface:
    pass


class AuthTokenRepo(AuthTokenRepoInterface):
    ACCESS_PREFIX = "access_token"
    REFRESH_PREFIX = "refresh_token"

    BLACKLIST_SUFFIX = "blacklist"
    ACTIVE_SUFFIX = "active"

    def __init__(self, client: CacheClientInterface) -> None:
        self.client = client

    async def blacklist_access_token(self, token: str) -> None:
        await self._set_blacklist(
            self.ACCESS_PREFIX,
            token,
            settings.access_token_ttl,
        )

    async def blacklist_refresh_token(self, token: str) -> None:
        await self._set_blacklist(
            self.REFRESH_PREFIX,
            token,
            settings.refresh_token_ttl,
        )

    async def is_access_token_blacklisted(self, token: str) -> bool:
        return await self._check_blacklist(self.ACCESS_PREFIX, token)

    async def is_refresh_token_blacklisted(self, token: str) -> bool:
        return await self._check_blacklist(self.REFRESH_PREFIX, token)

    async def _set_blacklist(self, prefix: str, token: str, ttl: int) -> None:
        key = self.client.build_cache_key(prefix, token, self.BLACKLIST_SUFFIX)
        await self.client.set_cache(
            key=key,
            data={},
            ttl=ttl,
        )

    async def _check_blacklist(self, prefix: str, token: str) -> bool:
        key = self.client.build_cache_key(prefix, token, self.BLACKLIST_SUFFIX)
        token_data = await self.client.get_cache(key)
        return token_data is not None


async def get_auth_token_repository(
    cache_client: Annotated[CacheClientInterface, Depends(get_redis_client)],
) -> AuthTokenRepoInterface:
    return AuthTokenRepo(cache_client)
