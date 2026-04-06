import uuid
from typing import AsyncGenerator, Awaitable, Callable

from aiohttp import ClientSession
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from pytest import fixture
from pytest_asyncio import fixture as async_fixture

from src_api.tests.functional.settings import test_settings

EsWriteDataType = Callable[[str, list[dict]], Awaitable[None]]
MakeGetRequestType = Callable[[str, dict | None], Awaitable[tuple[dict, int]]]


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
    async def inner(path: str, query_data: dict | None = None) -> tuple[dict, int]:
        aiohttp_session = ClientSession()
        if not query_data:
            query_data = {}

        url = test_settings.movies_api_base_url + path
        async with aiohttp_session.get(url, **query_data) as response:
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
    es_data = [
        {
            "id": str(uuid.uuid4()),
            "title": "Star Slammer",
            "description": "Two women who have been unjustly confined to a prison.",
            "imdb_rating": 3.5,
            "genres": ["Action", "Sci-Fi", "Comedy"],
            "directors_names": ["Fred Olen Ray"],
            "actors_names": ["Suzy Stokey"],
            "writers_names": ["Fred Olen Ray"],
            "directors": [
                {"id": "a2fd6df4-9f3c-4a26-8d59-914470d2aea0", "name": "Fred Olen Ray"},
            ],
            "actors": [
                {"id": "a91ff1c9-98a3-46af-a0d0-e9f2a2b4f51e", "name": "Suzy Stokey"},
            ],
            "writers": [
                {"id": "a2fd6df4-9f3c-4a26-8d59-914470d2aea0", "name": "Fred Olen Ray"},
            ],
        }
        for _ in range(60)
    ]
    bulk_query: list[dict] = []
    for row in es_data:
        data = {"_index": test_settings.elastic_movies_index_name, "_id": row["id"]}
        data.update({"_source": row})  # ty: ignore
        bulk_query.append(data)

    return bulk_query
