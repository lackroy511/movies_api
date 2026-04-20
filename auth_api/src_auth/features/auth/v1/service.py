from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request, Response

from src_auth.core.exc.exceptions import InvalidCredentialsError
from src_auth.core.security.cookies import set_token_cookie
from src_auth.core.security.hash_pass import verify_password
from src_auth.core.security.jwt import create_token
from src_auth.features.auth.v1.repository import (
    TokenBlacklistRepoInterface,
    TokenVersionRepoInterface,
    get_blacklist_token_repository,
    get_version_token_repository,
    AuthHistoryRepoInterface,
    get_auth_history_repository,
)
from src_auth.features.shared.dto import UserDTO
from src_auth.features.users.v1.service import UserService, get_user_service


class AuthService:
    def __init__(
        self,
        blacklist_repo: TokenBlacklistRepoInterface,
        version_repo: TokenVersionRepoInterface,
        auth_history_repo: AuthHistoryRepoInterface,
        user_service: UserService,
    ) -> None:
        self.blacklist_repo = blacklist_repo
        self.version_repo = version_repo
        self.auth_history_repo = auth_history_repo

        self.user_service = user_service

    async def register_user(
        self,
        email: str,
        first_name: str,
        last_name: str | None,
        password: str,
    ) -> UserDTO:

        # TODO: Назначить роль пользователю по умолчанию

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
        async with self.auth_history_repo.session.begin():
            user = await self.user_service.get_user_by_email(email)
            if not verify_password(password, user.password_hash):
                raise InvalidCredentialsError("Invalid credentials")

            user_agent = request.headers.get("user-agent", "Unknown user-agent")
            await self.auth_history_repo.create_auth_entry(user.id, user_agent)
            
            # TODO: Получать роли пользователя
            roles = ["regular_user"]
            token_version = await self._get_token_version(user_id=user.id)

            access_token = create_token(user.id, roles, "access", token_version)
            refresh_token = create_token(user.id, roles, "refresh", token_version)
            set_token_cookie(response, access_token, refresh_token)

            return user

    async def _get_token_version(self, user_id: UUID) -> int:
        ver = await self.version_repo.get_user_token_version(user_id)
        if not ver:
            ver = await self.version_repo.create_user_token_version(user_id)

        return ver.version


async def get_auth_service(
    blacklist_repo: Annotated[
        TokenBlacklistRepoInterface,
        Depends(get_blacklist_token_repository),
    ],
    version_repo: Annotated[
        TokenVersionRepoInterface,
        Depends(get_version_token_repository),
    ],
    auth_history_repo: Annotated[
        AuthHistoryRepoInterface,
        Depends(get_auth_history_repository),
    ],
    user_service: Annotated[
        UserService,
        Depends(get_user_service),
    ],
) -> AuthService:

    return AuthService(
        blacklist_repo=blacklist_repo,
        version_repo=version_repo,
        auth_history_repo=auth_history_repo,
        user_service=user_service,
    )
