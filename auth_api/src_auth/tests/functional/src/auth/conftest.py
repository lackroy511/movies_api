from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src_auth.features.users.v1.models import User
from sqlalchemy import delete
from pytest_asyncio import fixture as async_fixture


@async_fixture
async def clear_users_table(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    query = delete(User).where(User.id.isnot(None))
    await db_session.execute(query)
    await db_session.commit()
    yield
