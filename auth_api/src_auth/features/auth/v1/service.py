from fastapi import Depends
from typing import Annotated
from src_auth.features.shared.dto import UserDTO

from src_auth.features.users.v1.service import UserService, get_user_service
from src_auth.features.auth.v1.repository import AuthRepoInterface, get_auth_repository


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
        return await self.user_service.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )


async def get_auth_service(
    auth_repo: Annotated[AuthRepoInterface, Depends(get_auth_repository)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> AuthService:
    return AuthService(auth_repo=auth_repo, user_service=user_service)