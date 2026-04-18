from typing import Annotated

from fastapi import Depends

from src_auth.core.security.hash_pass import hash_password
from src_auth.features.shared.dto import UserDTO
from src_auth.features.users.v1.dto import CreateUserDTO
from src_auth.features.users.v1.repository import (
    UserRepoInterface,
    get_user_repository,
)


class UserService:
    def __init__(self, repository: UserRepoInterface) -> None:
        self.repository = repository

    async def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str | None,
        password: str,
    ) -> UserDTO:
        to_create = CreateUserDTO(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hash_password(password),
        )
        created_user = await self.repository.create(to_create)
        await self.repository.session.commit()
        return created_user


async def get_user_service(
    user_repository: Annotated[UserRepoInterface, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository=user_repository)
