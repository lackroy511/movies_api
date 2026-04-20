from abc import ABC, abstractmethod
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.core.db.sql_alch import get_db_session
from src_auth.features.roles.v1.dto import RoleDTO, CreateRoleDTO
from src_auth.features.roles.v1.models import Role, RoleName, user_roles


class RoleRepositoryInterface(ABC):
    @abstractmethod
    async def create_role(
        self,
        role: CreateRoleDTO,
    ) -> RoleDTO:
        pass

    @abstractmethod
    async def get_all_roles(self) -> list[RoleDTO]:
        pass

    @abstractmethod
    async def get_all_user_roles(self, user_id: UUID) -> list[RoleDTO]:
        pass

    @abstractmethod
    async def get_role_by_id(self, role_id: UUID) -> RoleDTO | None:
        pass

    @abstractmethod
    async def update_role(
        self,
        role_id: UUID,
        name: RoleName | None = None,
        description: str | None = None,
    ) -> RoleDTO | None:
        pass

    @abstractmethod
    async def delete_role(self, role_id: UUID) -> bool:
        pass

    @abstractmethod
    async def assign_user_to_role(self, user_id: UUID, role_id: UUID) -> None:
        pass

    @abstractmethod
    async def is_user_assigned_to_role(self, user_id: UUID, role_id: UUID) -> bool:
        pass

    @abstractmethod
    async def revoke_user_from_role(self, user_id: UUID, role_id: UUID) -> None:
        pass


class RoleRepository(RoleRepositoryInterface):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_role(
        self,
        role: CreateRoleDTO,
    ) -> RoleDTO:
        query = (
            insert(Role)
            .values(name=role.name, description=role.description)
            .returning(Role)
        )
        result = await self.session.execute(query)
        created = result.scalar_one()
        return RoleDTO(
            id=created.id,
            name=created.name,
            description=created.description,
        )

    async def get_all_roles(self) -> list[RoleDTO]:
        query = select(Role)
        result = await self.session.execute(query)
        roles = result.scalars().all()
        return [RoleDTO(id=r.id, name=r.name, description=r.description) for r in roles]

    async def get_all_user_roles(self, user_id: UUID) -> list[RoleDTO]:
        query = (
            select(Role)
            .join(user_roles, Role.id == user_roles.c.role_id)
            .where(user_roles.c.user_id == user_id)
        )
        result = await self.session.execute(query)
        roles = result.scalars().all()
        return [RoleDTO(id=r.id, name=r.name, description=r.description) for r in roles]

    async def get_role_by_id(self, role_id: UUID) -> RoleDTO | None:
        query = select(Role).where(Role.id == role_id)
        result = await self.session.execute(query)
        role = result.scalar_one_or_none()
        if not role:
            return None
        return RoleDTO(id=role.id, name=role.name, description=role.description)

    async def update_role(
        self,
        role_id: UUID,
        name: RoleName | None = None,
        description: str | None = None,
    ) -> RoleDTO | None:
        update_values = {}
        if name is not None:
            update_values["name"] = name
        if description is not None:
            update_values["description"] = description

        if not update_values:
            return await self.get_role_by_id(role_id)

        query = (
            update(Role)
            .where(Role.id == role_id)
            .values(**update_values)
            .returning(Role)
        )
        result = await self.session.execute(query)
        role = result.scalar_one_or_none()
        if not role:
            return None
        return RoleDTO(id=role.id, name=role.name, description=role.description)

    async def delete_role(self, role_id: UUID) -> bool:
        query = delete(Role).where(Role.id == role_id).returning(Role.id)
        result = await self.session.execute(query)
        deleted_id = result.scalar_one_or_none()
        return deleted_id is not None

    async def assign_user_to_role(self, user_id: UUID, role_id: UUID) -> None:
        query = insert(user_roles).values(user_id=user_id, role_id=role_id)
        await self.session.execute(query)

    async def is_user_assigned_to_role(self, user_id: UUID, role_id: UUID) -> bool:
        query = select(user_roles).where(
            user_roles.c.user_id == user_id,
            user_roles.c.role_id == role_id,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def revoke_user_from_role(self, user_id: UUID, role_id: UUID) -> None:
        query = delete(user_roles).where(
            user_roles.c.user_id == user_id,
            user_roles.c.role_id == role_id,
        )
        await self.session.execute(query)


async def get_role_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> RoleRepositoryInterface:
    return RoleRepository(session)
