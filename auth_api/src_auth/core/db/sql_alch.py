from datetime import datetime
from typing import Any, AsyncGenerator
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData, Uuid, func
from sqlalchemy.engine import Result
from sqlalchemy.exc import DBAPIError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src_auth.core.config.settings import settings
from src_auth.utils.backoff import Backoff

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=naming_convention)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    metadata = metadata

    id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


RETRY_EXCEPTIONS = (
    OperationalError,
    DBAPIError,
)


class BackoffAsyncSession(AsyncSession):
    @Backoff(RETRY_EXCEPTIONS)
    async def execute(self, *args: Any, **kwargs: Any) -> Result[Any]:  # noqa: ANN401
        return await super().execute(*args, **kwargs)

    async def commit(self) -> None:
        try:
            await super().commit()
        except SQLAlchemyError:
            try:
                await self.rollback()
            finally:
                raise


engine = create_async_engine(settings.db_url)
sessionmaker = async_sessionmaker(
    engine,
    class_=BackoffAsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session
