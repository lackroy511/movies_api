from src_auth.core.security.sso import OAuthProviderType
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends

from src_auth.core.config.settings import settings
from src_auth.core.db.cache import CacheClientInterface, get_redis_client
from src_auth.core.exc.exceptions import (
    InvalidCredentialsError,
    InvalidTokenOrExpiredTokenError,
)
from src_auth.core.security.hash_pass import verify_password
from src_auth.core.security.jwt import (
    TokenPayload,
    TokenType,
    create_token,
    verify_token,
)
from src_auth.features.auth.v1.dto import OAuthAccountDTO
from src_auth.features.auth.v1.repository import (
    OAuthAccountRepoInterface,
    TokenBlacklistRepoInterface,
    TokenVersionRepoInterface,
    get_blacklist_token_repository,
    get_oauth_account_repository,
    get_version_token_repository,
)
from src_auth.features.roles.v1.service import RoleService, get_role_service
from src_auth.features.shared.dto import UserDTO
from src_auth.features.users.v1.service import UserService, get_user_service


class AuthService:
    def __init__(
        self,
        oauth_service: OAuthService,
        session_service: SessionService,
        user_service: UserService,
        role_service: RoleService,
    ) -> None:
        self.oauth_service = oauth_service
        self.session_service = session_service
        self.user_service = user_service
        self.role_service = role_service

    async def register_user(
        self,
        email: str,
        first_name: str,
        last_name: str | None,
        password: str,
    ) -> UserDTO:
        return await self.user_service.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

    async def oauth_login_user(
        self,
        email: str,
        first_name: str | None,
        last_name: str | None,
        provider: OAuthProviderType,
        provider_user_id: str,
        user_agent: str,
    ) -> tuple[UserDTO, str, str]:
        user = await self._resolve_oauth_user(
            email,
            first_name,
            last_name,
            provider,
            provider_user_id,
        )
        return await self._process_login(user, user_agent)

    async def login_user(
        self,
        email: str,
        password: str,
        user_agent: str,
    ) -> tuple[UserDTO, str, str]:
        user = await self.user_service.get_user_by_email(email)
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        return await self._process_login(user, user_agent)

    async def refresh_tokens(
        self,
        access: str | None,
        refresh: str | None,
    ) -> tuple[str, str]:
        if not refresh:
            raise InvalidTokenOrExpiredTokenError("Refresh token is missing")

        payload = self.session_service.decode_token(refresh, "refresh")

        user_uuid = UUID(payload.user_id)
        actual_ver = await self.session_service.get_or_create_token_version(user_uuid)
        roles = await self._get_user_roles(user_uuid)

        await self.session_service.verify_session(payload, refresh)
        await self.session_service.blacklist_tokens(payload.user_id, access, refresh)
        new_access, new_refresh = await self.session_service.create_session_tokens(
            user_uuid,
            roles,
            actual_ver,
        )
        return new_access, new_refresh

    async def logout_user(
        self,
        access: str | None,
        refresh: str | None,
    ) -> None:
        if not access:
            raise InvalidTokenOrExpiredTokenError("No access token provided")

        payload = self.session_service.decode_token(access, "access")
        await self.session_service.verify_session(payload, access)
        await self.session_service.blacklist_tokens(payload.user_id, access, refresh)

    async def logout_all_user_sessions(
        self,
        access: str | None,
    ) -> None:
        if not access:
            raise InvalidTokenOrExpiredTokenError("No access token provided")

        payload = self.session_service.decode_token(access, "access")
        user_uuid = UUID(payload.user_id)
        await self.session_service.verify_session(payload, access)
        await self.session_service.revoke_all_sessions(user_uuid)

    async def _get_user_roles(self, user_id: UUID) -> list[str]:
        roles = await self.role_service.get_all_user_roles(user_id)
        return [role.name for role in roles]

    async def _resolve_oauth_user(
        self,
        email: str,
        first_name: str | None,
        last_name: str | None,
        provider: OAuthProviderType,
        provider_user_id: str,
    ) -> UserDTO:
        oauth_account = await self.oauth_service.get_oauth_user_account(
            provider=provider,
            provider_user_id=provider_user_id,
        )
        if oauth_account:
            return await self.user_service.get_user_by_id(oauth_account.user_id)

        user = await self.user_service.get_or_create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=None,
        )
        await self.oauth_service.get_or_create_oauth_account(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
        )
        return user

    async def _process_login(
        self,
        user: UserDTO,
        user_agent: str,
    ) -> tuple[UserDTO, str, str]:
        await self.user_service.create_auth_entry(user.id, user_agent)
        token_ver = await self.session_service.get_or_create_token_version(user.id)
        roles = await self._get_user_roles(user.id)
        access, refresh = await self.session_service.create_session_tokens(
            user.id,
            roles,
            token_ver,
        )
        return user, access, refresh


class SessionService:
    TOKEN_VER_PREFIX = "token_version"

    def __init__(
        self,
        blacklist_repo: TokenBlacklistRepoInterface,
        version_repo: TokenVersionRepoInterface,
        cache_client: CacheClientInterface,
    ) -> None:
        self.blacklist_repo = blacklist_repo
        self.version_repo = version_repo
        self.cache_client = cache_client

    async def create_session_tokens(
        self,
        user_uuid: UUID,
        roles: list[str],
        token_ver: int,
    ) -> tuple[str, str]:
        access_token = create_token(user_uuid, roles, "access", token_ver)
        refresh_token = create_token(user_uuid, roles, "refresh", token_ver)
        return access_token, refresh_token

    async def verify_session(self, payload: TokenPayload, token: str | None) -> None:
        user_uuid = UUID(payload.user_id)
        actual_ver = await self.get_or_create_token_version(user_uuid)

        if payload.ver != actual_ver:
            raise InvalidTokenOrExpiredTokenError("Invalid token version")

        if token and await self.blacklist_repo.is_token_blacklisted(
            token,
            payload.user_id,
        ):
            raise InvalidTokenOrExpiredTokenError("Token is blacklisted")

    async def blacklist_tokens(
        self,
        user_id: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        if access_token:
            await self.blacklist_repo.blacklist_access_token(access_token, user_id)
        if refresh_token:
            await self.blacklist_repo.blacklist_refresh_token(refresh_token, user_id)

    async def revoke_all_sessions(self, user_id: UUID) -> None:
        await self.version_repo.increment_user_token_version(user_id)
        await self._delete_token_version_from_cache(user_id)

    async def get_or_create_token_version(
        self,
        user_id: UUID,
    ) -> int:
        version = await self._get_token_version_from_cache(user_id)
        if version:
            return version

        ver = await self.version_repo.get_or_create_token_version(user_id)

        await self._set_token_version_to_cache(user_id, ver.version)
        return ver.version

    def decode_token(self, token: str, token_type: TokenType) -> TokenPayload:
        try:
            return verify_token(token, token_type)
        except jwt.PyJWTError, ValueError:
            raise InvalidTokenOrExpiredTokenError("Invalid or expired token") from None

    async def _get_token_version_from_cache(self, user_id: UUID) -> int | None:
        cache_key = self.cache_client.build_cache_key(self.TOKEN_VER_PREFIX, user_id)
        version = await self.cache_client.get_cache(cache_key)
        if version is None:
            return None

        if not isinstance(version, int):
            raise ValueError("Token version must be an integer") from None

        return version

    async def _set_token_version_to_cache(self, user_id: UUID, version: int) -> None:
        cache_key = self.cache_client.build_cache_key(self.TOKEN_VER_PREFIX, user_id)
        await self.cache_client.set_cache(cache_key, version, settings.access_token_ttl)

    async def _delete_token_version_from_cache(self, user_id: UUID) -> None:
        cache_key = self.cache_client.build_cache_key(self.TOKEN_VER_PREFIX, user_id)
        await self.cache_client.delete_cache(cache_key)


class OAuthService:
    def __init__(
        self,
        oauth_repo: OAuthAccountRepoInterface,
    ) -> None:
        self.oauth_repo = oauth_repo

    async def get_or_create_oauth_account(
        self,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
    ) -> OAuthAccountDTO:
        oauth_account = OAuthAccountDTO(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
        )
        return await self.oauth_repo.get_or_create_oauth_account(oauth_account)

    async def create_oauth_account(
        self,
        user_id: UUID,
        provider: str,
        provider_user_id: str,
    ) -> OAuthAccountDTO:
        new_oauth_account = OAuthAccountDTO(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
        )
        return await self.oauth_repo.create_oauth_account(new_oauth_account)

    async def get_oauth_user_account(
        self,
        provider: str,
        provider_user_id: str,
    ) -> OAuthAccountDTO | None:
        return await self.oauth_repo.get_oauth_account(
            provider=provider,
            provider_user_id=provider_user_id,
        )


async def get_auth_service(
    oauth_service: Annotated[OAuthService, Depends(get_oauth_service)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> AuthService:
    return AuthService(
        oauth_service=oauth_service,
        session_service=session_service,
        user_service=user_service,
        role_service=role_service,
    )


async def get_session_service(
    blacklist_repo: Annotated[
        TokenBlacklistRepoInterface,
        Depends(get_blacklist_token_repository),
    ],
    version_repo: Annotated[
        TokenVersionRepoInterface,
        Depends(get_version_token_repository),
    ],
    cache_client: Annotated[
        CacheClientInterface,
        Depends(get_redis_client),
    ],
) -> SessionService:
    return SessionService(
        blacklist_repo=blacklist_repo,
        version_repo=version_repo,
        cache_client=cache_client,
    )


async def get_oauth_service(
    oauth_repo: Annotated[
        OAuthAccountRepoInterface,
        Depends(get_oauth_account_repository),
    ],
) -> OAuthService:
    return OAuthService(oauth_repo)
