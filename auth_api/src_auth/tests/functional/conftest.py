import pytest
from typing import AsyncGenerator, Callable, Awaitable
import redis.asyncio as aioredis
from pytest_asyncio import fixture as async_fixture
from src_auth.tests.functional.settings import test_settings
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)
from aiohttp import ClientSession
from alembic.config import Config
from alembic import command


MakeGetRequestType = Callable[[str, dict | None], Awaitable[tuple[dict, int]]]
MakePostRequestType = Callable[[str, dict | None], Awaitable[tuple[dict, int]]]


# http fixtures
@async_fixture
def make_get_request(aiohttp_session: ClientSession) -> MakeGetRequestType:
    async def inner(path: str, params: dict | None = None) -> tuple[dict, int]:
        if not params:
            params = {}

        url = test_settings.auth_api_base_url + path
        async with aiohttp_session.get(url, params=params) as response:
            body = await response.json()
            status = response.status

        return body, status

    return inner


@async_fixture
def make_post_request(aiohttp_session: ClientSession) -> MakePostRequestType:
    async def inner(path: str, data: dict | None = None) -> tuple[dict, int]:
        if not data:
            data = {}

        url = test_settings.auth_api_base_url + path
        async with aiohttp_session.post(url, json=data) as response:
            body = await response.json()
            status = response.status

        return body, status

    return inner


@async_fixture(scope="session")
async def aiohttp_session() -> AsyncGenerator[ClientSession, None]:
    session = ClientSession()
    yield session
    await session.close()


# redis client fixture
@async_fixture
async def redis_connection(
    redis_client: aioredis.Redis,
) -> AsyncGenerator[aioredis.Redis, None]:
    await redis_client.flushall()
    yield redis_client


@async_fixture(scope="session")
async def redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    pool = aioredis.ConnectionPool.from_url(
        test_settings.redis_base_url,
        max_connections=2,
    )
    client = aioredis.Redis(connection_pool=pool)
    yield client
    await client.aclose()


# db session fixture
@async_fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.connect() as connection:
        async_session = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
        )
        async with async_session() as session:
            async with session.begin():
                yield session


@async_fixture(scope="session")
async def engine(apply_migrations: None) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(test_settings.db_url, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def apply_migrations() -> None:
    alembic_cfg = Config(test_settings.base_dir / "alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_settings.db_url)
    command.upgrade(alembic_cfg, "head")
