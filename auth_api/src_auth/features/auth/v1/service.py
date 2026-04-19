from typing import Annotated

from fastapi import Depends, Response

from src_auth.core.exc.exceptions import InvalidCredentialsError
from src_auth.core.security.cookies import set_token_cookie
from src_auth.core.security.hash_pass import verify_password
from src_auth.core.security.jwt import create_token
from src_auth.features.auth.v1.repository import AuthRepoInterface, get_auth_repository
from src_auth.features.shared.dto import UserDTO
from src_auth.features.users.v1.service import UserService, get_user_service


class AuthService:
    def __init__(
        self,
        auth_repo: AuthRepoInterface,
        user_service: UserService,
    ) -> None:
        self.auth_repo = auth_repo
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
        email: str,
        password: str,
        response: Response,
    ) -> UserDTO:
        user = await self.user_service.get_user_by_email(email)
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")
        
        # TODO: Получать роли пользователя
        
        roles = ["regular_user"]
        access_token = create_token(user.id, roles, "access")
        refresh_token = create_token(user.id, roles, "refresh")
        set_token_cookie(response, access_token, refresh_token)
        
        # TODO: Сохранять токены в Redis
        
        return user


async def get_auth_service(
    auth_repo: Annotated[AuthRepoInterface, Depends(get_auth_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> AuthService:
    return AuthService(auth_repo=auth_repo, user_service=user_service)
