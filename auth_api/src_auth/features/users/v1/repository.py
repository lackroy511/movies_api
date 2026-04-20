from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Depends
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.core.db.sql_alch import get_db_session
from src_auth.core.exc.exceptions import UserAlreadyExistsError
from src_auth.features.shared.dto import UserDTO
from src_auth.features.users.v1.dto import CreateUserDTO
from src_auth.features.users.v1.models import User


class UserRepoInterface(ABC):
    @abstractmethod
    async def create(self, user: CreateUserDTO) -> UserDTO:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserDTO | None:
        pass


class UserRepo(UserRepoInterface):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: CreateUserDTO) -> UserDTO:
        query = (
            insert(User)
            .values(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                password_hash=user.password_hash,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
            )
            .returning(User)
        )
        try:
            result = await self.session.execute(query)
        except IntegrityError as e:
            if getattr(e.orig, "pgcode", None) == "23505":
                raise UserAlreadyExistsError() from None

            raise

        created = result.scalar_one()
        return self._transform_to_dto(created)

    async def get_by_email(self, email: str) -> UserDTO | None:
        query = select(User).where(
            User.email == email,
            User.is_active.is_(True),
        )
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None

        return self._transform_to_dto(user)

    def _transform_to_dto(self, user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password_hash=user.password_hash,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepoInterface:
    return UserRepo(session=session)
