from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src_auth.features.roles.v1.dto import RoleDTO
from src_auth.features.roles.v1.repository import (
    RoleRepositoryInterface,
    get_role_repository,
)


class RoleService:
    def __init__(self, repository: RoleRepositoryInterface) -> None:
        self.repository = repository

    async def get_all_user_roles(self, user_id: UUID) -> list[RoleDTO]:
        return await self.repository.get_all_user_roles(user_id=user_id)


async def get_role_service(
    role_repo: Annotated[RoleRepositoryInterface, Depends(get_role_repository)],
) -> RoleService:
    return RoleService(role_repo)
