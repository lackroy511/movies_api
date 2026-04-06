import random
import uuid
from typing import AsyncGenerator, Awaitable, Callable

from aiohttp import ClientSession
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from pytest import fixture
from pytest_asyncio import fixture as async_fixture
from faker import Faker

from src_api.tests.functional.settings import test_settings

EsWriteDataType = Callable[[str, list[dict]], Awaitable[None]]
MakeGetRequestType = Callable[[str, dict | None], Awaitable[tuple[dict, int]]]

fake = Faker()


@async_fixture
def es_write_data(
    es_client: AsyncElasticsearch,
) -> EsWriteDataType:
    async def inner(index: str, data: list[dict]) -> None:
        if await es_client.indices.exists(
            index=index,
        ):
            await es_client.indices.delete(
                index=index,
            )

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


@async_fixture(scope="function")
async def aiohttp_session() -> AsyncGenerator[ClientSession, None]:
    async with ClientSession() as session:
        yield session


@fixture
def movies_es_data() -> list[dict]:
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
    for _ in range(test_settings.count_of_test_movies):
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
