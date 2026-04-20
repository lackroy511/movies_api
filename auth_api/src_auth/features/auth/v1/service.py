from typing import Annotated

from fastapi import Depends, Response, Request

from src_auth.core.exc.exceptions import InvalidCredentialsError
from src_auth.core.security.cookies import set_token_cookie
from src_auth.core.security.hash_pass import verify_password
from src_auth.core.security.jwt import create_token
from src_auth.features.auth.v1.repository import (
    get_blacklist_token_repository,
    TokenBlacklistRepoInterface,
    TokenVersionRepoInterface, get_version_token_repository,
)
from src_auth.features.shared.dto import UserDTO
from src_auth.features.users.v1.service import UserService, get_user_service


class AuthService:
    def __init__(
        self,
        blacklist_repo: TokenBlacklistRepoInterface,
        version_repo: TokenVersionRepoInterface,
        user_service: UserService,
    ) -> None:
        self.blacklist_repo = blacklist_repo
        self.version_repo = version_repo

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
        user = await self.user_service.get_user_by_email(email)
        # user_agent = request.headers.get("user-agent")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")

        # TODO: Получать роли пользователя
        roles = ["regular_user"]

        token_version = 0

        access_token = create_token(user.id, roles, "access", token_version)
        refresh_token = create_token(user.id, roles, "refresh", token_version)
        set_token_cookie(response, access_token, refresh_token)

        return user


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
) -> AuthService:

    return AuthService(
        blacklist_repo=blacklist_repo,
        version_repo=version_repo,
        user_service=user_service,
    )
