import random
import uuid
from typing import AsyncGenerator, Awaitable, Callable

import redis.asyncio as aioredis
from aiohttp import ClientSession
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from faker import Faker
from pytest import fixture
from pytest_asyncio import fixture as async_fixture

from src_api.tests.functional.settings import test_settings

EsWriteDataType = Callable[[str, list[dict]], Awaitable[None]]
MakeGetRequestType = Callable[[str, dict | None], Awaitable[tuple[dict, int]]]
CreateMoviesDataType = Callable[[int], list[dict]]

fake = Faker()


@async_fixture
def es_write_data(
    es_client: AsyncElasticsearch,
    redis_client: aioredis.Redis,
) -> EsWriteDataType:
    async def inner(index: str, data: list[dict]) -> None:
        await redis_client.flushall()
        
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)

        await es_client.indices.create(
            index=index,
            **test_settings.elastic_movies_index_mapping,
        )

        updated, errors = await async_bulk(client=es_client, actions=data)
        await es_client.indices.refresh(index=index)
        if errors:
            raise Exception("Ошибка записи данных в Elasticsearch")

    return inner


@async_fixture(scope="session")
async def es_client() -> AsyncGenerator[AsyncElasticsearch, None]:
    es_client = AsyncElasticsearch(
        hosts=test_settings.elastic_base_url,
        verify_certs=False,
    )
    yield es_client
    await es_client.close()


@async_fixture(scope="session")
async def redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    pool = aioredis.ConnectionPool.from_url(
        test_settings.redis_base_url,
        max_connections=2,
    )
    client = aioredis.Redis(connection_pool=pool)
    yield client
    await client.aclose()


@async_fixture
def make_get_request(aiohttp_session: ClientSession) -> MakeGetRequestType:
    async def inner(path: str, params: dict | None = None) -> tuple[dict, int]:
        aiohttp_session = ClientSession()
        if not params:
            params = {}

        url = test_settings.movies_api_base_url + path
        async with aiohttp_session.get(url, params=params) as response:
            body = await response.json()
            status = response.status

        return body, status

    return inner


@async_fixture(scope="session")
async def aiohttp_session() -> AsyncGenerator[ClientSession, None]:
    session = ClientSession()
    yield session
    await session.close()


@fixture
def create_movies_es_data() -> CreateMoviesDataType:
    def inner(movies_count: int) -> list[dict]:
        test_genres = [
            "Action",
            "Sci-Fi",
            "Comedy",
            "Drama",
            "Horror",
            "Thriller",
            "Romance",
        ]
        test_persons = [{"id": uuid.uuid4(), "name": fake.name()} for _ in range(120)]

        movies = []
        for _ in range(movies_count):
            actors = random.sample(test_persons, k=random.randint(1, 5))
            directors = random.sample(test_persons, k=random.randint(1, 5))
            writers = random.sample(test_persons, k=random.randint(1, 5))

            movie = {
                "id": str(uuid.uuid4()),
                "title": fake.catch_phrase(),
                "description": fake.paragraph(nb_sentences=3),
                "imdb_rating": random.uniform(1.0, 10.0),
                "genres": random.sample(test_genres, k=random.randint(1, 3)),
                "directors_names": [director["name"] for director in directors],
                "actors_names": [actor["name"] for actor in actors],
                "writers_names": [writer["name"] for writer in writers],
                "directors": directors,
                "actors": actors,
                "writers": writers,
            }
            movies.append(movie)

        bulk_query: list[dict] = []
        for row in movies:
            data = {"_index": test_settings.elastic_movies_index_name, "_id": row["id"]}
            data.update({"_source": row})
            bulk_query.append(data)

        return bulk_query

    return inner
