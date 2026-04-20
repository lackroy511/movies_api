from src_auth.core.db.sql_alch import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from src_auth.features.auth.v1.dto import TokenVersionDTO
from abc import abstractmethod
from src_auth.core.db.cache import CacheClientInterface, get_redis_client
from fastapi import Depends
from typing import Annotated

from src_auth.core.config.settings import settings


class TokenBlacklistRepoInterface:
    @abstractmethod
    async def blacklist_access_token(self, token: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def blacklist_refresh_token(self, token: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def is_token_blacklisted(self, token: str, user_id: str) -> bool:
        pass


class TokenBlacklistRepo(TokenBlacklistRepoInterface):
    PREFIX: str = "blacklisted_auth_token"

    def __init__(self, client: CacheClientInterface) -> None:
        self.client = client

    async def blacklist_access_token(self, token: str, user_id: str) -> None:
        key = self.client.build_cache_key(self.PREFIX, user_id, token)
        await self.client.set_cache(key, "1", ttl=settings.access_token_ttl)

    async def blacklist_refresh_token(self, token: str, user_id: str) -> None:
        key = self.client.build_cache_key(self.PREFIX, user_id, token)
        await self.client.set_cache(key, "1", ttl=settings.refresh_token_ttl)

    async def is_token_blacklisted(self, token: str, user_id: str) -> bool:
        key = self.client.build_cache_key(self.PREFIX, user_id, token)
        result = await self.client.get_cache(key)
        return result is not None


class TokenVersionRepoInterface:
    @abstractmethod
    async def get_user_token_version(self, user_id: str) -> TokenVersionDTO:
        pass

    @abstractmethod
    async def increment_user_token_version(self, user_id: str) -> None:
        pass
    
    @abstractmethod
    async def create_user_token_version(self, user_id: str) -> None:
        pass


class TokenVersionRepo(TokenVersionRepoInterface):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


async def get_blacklist_token_repository(
    cache_client: Annotated[CacheClientInterface, Depends(get_redis_client)],
) -> TokenBlacklistRepoInterface:
    return TokenBlacklistRepo(cache_client)
 
 
async def get_version_token_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenVersionRepoInterface:
    return TokenVersionRepo(session)