from typing import AsyncGenerator

from pytest_asyncio import fixture as async_fixture
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.features.users.v1.models import User, UserAuthHistory
from src_auth.tests.functional.settings import test_settings


@async_fixture
async def clear_users_table(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    query = delete(User).where(User.email != test_settings.admin_email)
    await db_session.execute(query)
    await db_session.commit()
    yield


@async_fixture
async def clear_auth_history_table(
    db_session: AsyncSession,
) -> AsyncGenerator[None, None]:
    query = delete(UserAuthHistory)
    await db_session.execute(query)
    await db_session.commit()
    yield
