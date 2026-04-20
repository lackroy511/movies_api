from abc import abstractmethod
from src_auth.core.db.cache import CacheClientInterface, get_redis_client
from fastapi import Depends
from typing import Annotated

from src_auth.core.config.settings import settings


class AuthTokenRepoInterface:
    @abstractmethod
    async def save_access_token(self, token: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def save_refresh_token(self, token: str, user_id: str) -> None:
        pass
        
    @abstractmethod
    async def is_access_token_active(self, token: str, user_id: str) -> bool:
        pass
        
    @abstractmethod
    async def is_refresh_token_active(self, token: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def blacklist_access_token(self, token: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def blacklist_refresh_token(self, token: str, user_id: str) -> None:
        pass

    @abstractmethod
    async def blacklist_all_user_tokens(self, user_id: str) -> None:
        pass


class AuthTokenRepo(AuthTokenRepoInterface):
    PREFIX: str = "auth_token"
    
    ACCESS_TYPE = "access_token"
    REFRESH_TYPE = "refresh_token"

    BLACKLIST_SUFFIX = "blacklist"
    ACTIVE_SUFFIX = "active"

    def __init__(self, client: CacheClientInterface) -> None:
        self.client = client


async def get_auth_token_repository(
    cache_client: Annotated[CacheClientInterface, Depends(get_redis_client)],
) -> AuthTokenRepoInterface:
    return AuthTokenRepo(cache_client)
