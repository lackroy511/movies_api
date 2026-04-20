from abc import ABC, abstractmethod
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.core.config.settings import settings
from src_auth.core.db.cache import CacheClientInterface, get_redis_client
from src_auth.core.db.sql_alch import get_db_session
from src_auth.features.auth.v1.dto import TokenVersionDTO
from src_auth.features.auth.v1.models import TokenVersion


class TokenBlacklistRepoInterface(ABC):
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


class TokenVersionRepoInterface(ABC):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    @abstractmethod
    async def create_user_token_version(self, user_id: UUID) -> TokenVersionDTO:
        pass
    
    @abstractmethod
    async def get_user_token_version(self, user_id: UUID) -> TokenVersionDTO | None:
        pass

    @abstractmethod
    async def increment_user_token_version(self, user_id: UUID) -> None:
        pass


class TokenVersionRepo(TokenVersionRepoInterface):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_user_token_version(self, user_id: UUID) -> TokenVersionDTO:
        query = (
            insert(TokenVersion)
            .values(user_id=user_id, version=0)
            .returning(TokenVersion)
        )
        result = await self.session.execute(query)
        created = result.scalar_one()
        return TokenVersionDTO(user_id=created.user_id, version=created.version) 
    
    async def get_user_token_version(self, user_id: UUID) -> TokenVersionDTO | None:
        query = select(TokenVersion).where(TokenVersion.user_id == user_id)
        result = await self.session.execute(query)
        token_ver = result.scalar_one_or_none()
        if token_ver is None:
            return None
            
        return TokenVersionDTO(user_id=token_ver.user_id, version=token_ver.version)

    async def increment_user_token_version(self, user_id: UUID) -> None:
        query = (
            update(TokenVersion)
            .where(TokenVersion.user_id == user_id)
            .values(version=TokenVersion.version + 1)
        )
        await self.session.execute(query)


async def get_blacklist_token_repository(
    cache_client: Annotated[CacheClientInterface, Depends(get_redis_client)],
) -> TokenBlacklistRepoInterface:
    return TokenBlacklistRepo(cache_client)


async def get_version_token_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenVersionRepoInterface:
    return TokenVersionRepo(session)
