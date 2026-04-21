from abc import ABC, abstractmethod
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.core.config.settings import settings
from src_auth.core.db.cache import CacheClientInterface, get_redis_client
from src_auth.core.db.sql_alch import get_db_session
from src_auth.features.auth.v1.dto import AuthHistoryDTO, TokenVersionDTO
from src_auth.features.auth.v1.models import AuthHistory, TokenVersion


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
        self.session = session

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


class AuthHistoryRepoInterface(ABC):
    @abstractmethod
    async def create_auth_entry(self, user_id: UUID, user_agent: str) -> None:
        pass

    @abstractmethod
    async def get_user_auth_history(self, user_id: UUID) -> list[AuthHistoryDTO]:
        pass


class AuthHistoryRepo(AuthHistoryRepoInterface):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_auth_entry(self, user_id: UUID, user_agent: str) -> None:
        query = (
            insert(AuthHistory)
            .values(user_id=user_id, user_agent=user_agent)
        )
        await self.session.execute(query)

    async def get_user_auth_history(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> list[AuthHistoryDTO]:
        query = (
            select(AuthHistory)
            .where(AuthHistory.user_id == user_id)
            .order_by(AuthHistory.auth_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        history = result.scalars().all()
        return [
            AuthHistoryDTO(
                user_id=h.user_id,
                user_agent=h.user_agent,
                auth_at=h.auth_at,
            )
            for h in history
        ]


async def get_version_token_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenVersionRepoInterface:
    return TokenVersionRepo(session)


async def get_blacklist_token_repository(
    cache_client: Annotated[CacheClientInterface, Depends(get_redis_client)],
) -> TokenBlacklistRepoInterface:
    return TokenBlacklistRepo(cache_client)


async def get_auth_history_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthHistoryRepoInterface:
    return AuthHistoryRepo(session)
