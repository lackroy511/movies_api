from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Request, Response

from src_auth.core.config.settings import settings
from src_auth.core.exc.exceptions import (
    InvalidCredentialsError,
    InvalidTokenOrExpiredTokenError,
)
from src_auth.core.security.cookies import set_token_cookie
from src_auth.core.security.hash_pass import verify_password
from src_auth.core.security.jwt import (
    TokenPayload,
    TokenType,
    create_token,
    verify_token,
)
from src_auth.features.auth.v1.repository import (
    TokenBlacklistRepoInterface,
    TokenVersionRepoInterface,
    get_blacklist_token_repository,
    get_version_token_repository,
)
from src_auth.features.roles.v1.service import RoleService, get_role_service
from src_auth.features.shared.dto import UserDTO
from src_auth.features.users.v1.service import UserService, get_user_service


class AuthService:
    def __init__(
        self,
        blacklist_repo: TokenBlacklistRepoInterface,
        version_repo: TokenVersionRepoInterface,
        user_service: UserService,
        role_service: RoleService,
    ) -> None:
        self.blacklist_repo = blacklist_repo
        self.version_repo = version_repo

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

    async def login_user(
        self,
        request: Request,
        email: str,
        password: str,
        response: Response,
    ) -> UserDTO:
        user = await self.user_service.get_user_by_email(email)
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        user_agent = request.headers.get("user-agent", "Unknown user-agent")
        await self.user_service.create_auth_entry(user.id, user_agent)

        token_version = await self._get_or_create_token_version(user_id=user.id)
        roles = await self._get_user_roles(user.id)

        new_access, new_refresh = await self._create_new_tokens(
            user.id,
            roles,
            token_version,
        )
        set_token_cookie(response, new_access, new_refresh)
        return user

    async def refresh_tokens(
        self,
        request: Request,
        response: Response,
    ) -> None:
        access = request.cookies.get(settings.access_cookie_name)
        refresh = request.cookies.get(settings.refresh_cookie_name, "wrong token")
        payload = await self._get_token_payload(refresh, "refresh")

        user_uuid = UUID(payload.user_id)
        actual_ver = await self._get_or_create_token_version(user_uuid)
        roles = await self._get_user_roles(user_uuid)

        await self._check_token_version(payload, actual_ver)
        await self._is_token_blacklisted(refresh, payload.user_id)
        await self._blacklist_old_tokens(payload.user_id, access, refresh)

        new_access, new_refresh = await self._create_new_tokens(
            user_uuid,
            roles,
            actual_ver,
        )
        set_token_cookie(response, new_access, new_refresh)

    async def _get_token_payload(
        self,
        token: str,
        token_type: TokenType,
    ) -> TokenPayload:
        try:
            return verify_token(token, token_type)
        except jwt.PyJWTError, ValueError:
            raise InvalidTokenOrExpiredTokenError("Invalid or expired token") from None

    async def _is_token_blacklisted(
        self,
        token: str,
        user_id: str,
    ) -> None:
        if await self.blacklist_repo.is_token_blacklisted(token, user_id):
            raise InvalidTokenOrExpiredTokenError("Token is blacklisted")

    async def _blacklist_old_tokens(
        self,
        user_id: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        if access_token:
            await self.blacklist_repo.blacklist_access_token(access_token, user_id)
        if refresh_token:
            await self.blacklist_repo.blacklist_refresh_token(refresh_token, user_id)

    async def _create_new_tokens(
        self,
        user_uuid: UUID,
        roles: list[str],
        token_ver: int,
    ) -> tuple[str, str]:
        access_token = create_token(user_uuid, roles, "access", token_ver)
        refresh_token = create_token(user_uuid, roles, "refresh", token_ver)
        return access_token, refresh_token

    async def _check_token_version(self, payload: TokenPayload, version: int) -> None:
        if payload.ver != version:
            raise InvalidTokenOrExpiredTokenError("Invalid token version")

    async def _get_or_create_token_version(self, user_id: UUID) -> int:
        ver = await self.version_repo.get_user_token_version(user_id)
        if not ver:
            ver = await self.version_repo.create_user_token_version(user_id)

        return ver.version

    async def _get_user_roles(self, user_id: UUID) -> list[str]:
        roles = await self.role_service.get_all_user_roles(user_id)
        return [role.name for role in roles]


async def get_auth_service(
    blacklist_repo: Annotated[
        TokenBlacklistRepoInterface,
        Depends(get_blacklist_token_repository),
    ],
    version_repo: Annotated[
        TokenVersionRepoInterface,
        Depends(get_version_token_repository),
    ],
    user_service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
    role_service: Annotated[
        RoleService,
        Depends(get_role_service),
    ],
) -> AuthService:
    return AuthService(
        blacklist_repo=blacklist_repo,
        version_repo=version_repo,
        user_service=user_service,
        role_service=role_service,
    )
