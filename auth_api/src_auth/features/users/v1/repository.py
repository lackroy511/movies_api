from src_auth.features.shared.dto import UserDTO
from src_auth.core.db.sql_alch import get_db_session
from fastapi import Depends
from typing import Annotated
from src_auth.features.users.v1.models import User
from src_auth.features.users.v1.dto import CreateUserDTO

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from abc import ABC, abstractmethod


class UserRepoInterface(ABC):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    @abstractmethod
    async def create(self, user: CreateUserDTO) -> UserDTO:
        pass


class UserRepo(UserRepoInterface):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session) 

    async def create(self, user: CreateUserDTO) -> UserDTO:
        query = (
            insert(User)
            .values(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                password_hash=user.password_hash,
                is_active=user.is_active,
            )
            .returning(User)
        )
        result = await self.session.execute(query)
        created = result.scalar_one()
        return UserDTO(
            id=created.id,
            email=created.email,
            first_name=created.first_name,
            last_name=created.last_name,
            is_active=created.is_active,
            created_at=created.created_at,
            updated_at=created.updated_at,
        )


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepoInterface:
    return UserRepo(session=session)
