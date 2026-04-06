import uuid
import random
import pytest
from elasticsearch import AsyncElasticsearch

from src_api.tests.functional.conftest import (
    CreateGenresDataType,
    EsWriteDataType,
    MakeGetRequestType,
)
from src_api.tests.functional.settings import test_settings


GENRES_ENDPOINT = "/api/v1/genres"
DEFAULT_GENRES_COUNT = 60


@pytest.mark.asyncio
async def test_default_list(
    create_genres_es_data: CreateGenresDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    genres_count = DEFAULT_GENRES_COUNT
    genres_data = create_genres_es_data(genres_count)
    await es_write_data(
        test_settings.elastic_genres_index_name,
        genres_data,
        test_settings.elastic_genres_index_mapping,
    )

    params = {"page_size": 10}
    body, status = await make_get_request(GENRES_ENDPOINT, params)

    assert status == 200
    assert body["total"] == genres_count
    assert body["page_number"] == 1
    assert body["has_next"] is True
    assert body["has_prev"] is False


@pytest.mark.asyncio
async def test_cached_list(
    create_genres_es_data: CreateGenresDataType,
    es_write_data: EsWriteDataType,
    es_client: AsyncElasticsearch,
    make_get_request: MakeGetRequestType,
) -> None:
    async def check_genres(
        page_size: int,
        expected_status: int,
        expected_total: int | None = None,
        detail: str | None = None,
    ) -> None:
        body, status = await make_get_request(
            GENRES_ENDPOINT,
            {"page_size": page_size},
        )
        assert status == expected_status
        if expected_total is not None:
            assert body["total"] == expected_total
        if detail is not None:
            assert body["detail"] == detail

    genres_count = DEFAULT_GENRES_COUNT
    page_size = 10
    await es_write_data(
        test_settings.elastic_genres_index_name,
        create_genres_es_data(genres_count),
        test_settings.elastic_genres_index_mapping,
    )
    # Запрос, данные кэшируются
    await check_genres(page_size, 200, expected_total=genres_count)
    await es_client.indices.delete(index=test_settings.elastic_genres_index_name)
    # Не попали в кэш
    await check_genres(page_size + 10, 500, detail="Elastic index not found error")
    # Так как индекс удален, получаем данные из кэша
    await check_genres(page_size, 200, expected_total=genres_count)


@pytest.mark.asyncio
async def test_get_by_id(
    create_genres_es_data: CreateGenresDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    genres_data = create_genres_es_data(1)
    await es_write_data(
        test_settings.elastic_genres_index_name,
        genres_data,
        test_settings.elastic_genres_index_mapping,
    )

    genre_id = genres_data[0]["_source"]["id"]
    body, status = await make_get_request(f"{GENRES_ENDPOINT}/{genre_id}", None)

    assert status == 200
    assert body["id"] == genre_id
    assert body["name"] == genres_data[0]["_source"]["name"]


@pytest.mark.asyncio
async def test_cached_get_by_id(
    create_genres_es_data: CreateGenresDataType,
    es_write_data: EsWriteDataType,
    es_client: AsyncElasticsearch,
    make_get_request: MakeGetRequestType,
) -> None:
    genres_data = create_genres_es_data(1)
    await es_write_data(
        test_settings.elastic_genres_index_name,
        genres_data,
        test_settings.elastic_genres_index_mapping,
    )

    genre_id = genres_data[0]["_source"]["id"]

    body, status = await make_get_request(f"{GENRES_ENDPOINT}/{genre_id}", None)
    assert status == 200
    assert body["id"] == genre_id

    await es_client.indices.delete(index=test_settings.elastic_genres_index_name)

    body, status = await make_get_request(f"{GENRES_ENDPOINT}/{genre_id}", None)
    assert status == 200
    assert body["id"] == genre_id


@pytest.mark.asyncio
async def test_non_existing_get_by_id(
    create_genres_es_data: CreateGenresDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    genres_data = create_genres_es_data(1)
    await es_write_data(
        test_settings.elastic_genres_index_name,
        genres_data,
        test_settings.elastic_genres_index_mapping,
    )

    genre_id = uuid.uuid4()
    body, status = await make_get_request(f"{GENRES_ENDPOINT}/{genre_id}", None)
    assert status == 404


@pytest.mark.parametrize(
    "page_number, page_size, expected_items_count, expected_has_next, expected_has_prev",  # noqa: E501
    [
        (1, 20, 20, True, False),
        (2, 20, 20, True, True),
        (3, 20, 20, False, True),
        (4, 20, 0, False, True),
        (5, 20, 0, False, False),
    ],
)
@pytest.mark.asyncio
async def test_pagination(
    create_genres_es_data: CreateGenresDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
    page_number: int,
    page_size: int,
    expected_items_count: int,
    expected_has_next: bool,
    expected_has_prev: bool,
) -> None:
    genres_count = 60
    genres_data = create_genres_es_data(genres_count)
    await es_write_data(
        test_settings.elastic_genres_index_name,
        genres_data,
        test_settings.elastic_genres_index_mapping,
    )

    params = {"page_number": page_number, "page_size": page_size}
    body, status = await make_get_request(GENRES_ENDPOINT, params)
    assert status == 200

    assert len(body["items"]) == expected_items_count
    assert body["has_next"] is expected_has_next
    assert body["has_prev"] is expected_has_prev

    if expected_items_count > 0:
        last_item_index = page_number * page_size - 1
        assert body["items"][-1]["id"] == genres_data[last_item_index]["_source"]["id"]


@pytest.mark.asyncio
async def test_search(
    create_genres_es_data: CreateGenresDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    genres_count = DEFAULT_GENRES_COUNT
    genres_data = create_genres_es_data(genres_count)
    await es_write_data(
        test_settings.elastic_genres_index_name,
        genres_data,
        test_settings.elastic_genres_index_mapping,
    )

    target_genre = random.choice(genres_data)["_source"]
    search_query = target_genre["name"]

    params = {"search": search_query}
    body, status = await make_get_request(GENRES_ENDPOINT, params)

    assert status == 200

    found_ids = [item["id"] for item in body["items"]]
    assert target_genre["id"] in found_ids
