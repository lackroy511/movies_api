import uuid
import random
import pytest
from elasticsearch import AsyncElasticsearch

from src_api.tests.functional.conftest import (
    CreatePersonsDataType,
    EsWriteDataType,
    MakeGetRequestType,
    CreateMoviesDataType,
)
from src_api.tests.functional.settings import test_settings


PERSONS_ENDPOINT = "/api/v1/persons"
DEFAULT_PERSONS_COUNT = 60


@pytest.mark.asyncio
async def test_default_list(
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    persons_count = DEFAULT_PERSONS_COUNT
    persons_data = create_persons_es_data(persons_count)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    params = {"page_size": 10}
    body, status = await make_get_request(PERSONS_ENDPOINT, params)

    assert status == 200
    assert body["total"] == persons_count
    assert body["page_number"] == 1
    assert body["has_next"] is True
    assert body["has_prev"] is False


@pytest.mark.asyncio
async def test_cached_list(
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    es_client: AsyncElasticsearch,
    make_get_request: MakeGetRequestType,
) -> None:
    async def check_persons(
        page_size: int,
        expected_status: int,
        expected_total: int | None = None,
        detail: str | None = None,
    ) -> None:
        body, status = await make_get_request(
            PERSONS_ENDPOINT,
            {"page_size": page_size},
        )
        assert status == expected_status
        if expected_total is not None:
            assert body["total"] == expected_total
        if detail is not None:
            assert body["detail"] == detail

    persons_count = DEFAULT_PERSONS_COUNT
    page_size = 10
    await es_write_data(
        test_settings.elastic_persons_index_name,
        create_persons_es_data(persons_count),
        test_settings.elastic_persons_index_mapping,
    )
    # Запрос, данные кэшируются
    await check_persons(page_size, 200, expected_total=persons_count)
    await es_client.indices.delete(index=test_settings.elastic_persons_index_name)
    # Не попали в кэш
    await check_persons(page_size + 10, 500, detail="Elastic index not found error")
    # Так как индекс удален, получаем данные из кэша
    await check_persons(page_size, 200, expected_total=persons_count)


@pytest.mark.asyncio
async def test_get_by_id(
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    persons_data = create_persons_es_data(1)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    person_id = persons_data[0]["_source"]["id"]
    body, status = await make_get_request(f"{PERSONS_ENDPOINT}/{person_id}", None)

    assert status == 200
    assert body["id"] == person_id
    assert body["full_name"] == persons_data[0]["_source"]["full_name"]


@pytest.mark.asyncio
async def test_cached_get_by_id(
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    es_client: AsyncElasticsearch,
    make_get_request: MakeGetRequestType,
) -> None:
    persons_data = create_persons_es_data(1)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    person_id = persons_data[0]["_source"]["id"]

    body, status = await make_get_request(f"{PERSONS_ENDPOINT}/{person_id}", None)
    assert status == 200
    assert body["id"] == person_id

    await es_client.indices.delete(index=test_settings.elastic_persons_index_name)

    body, status = await make_get_request(f"{PERSONS_ENDPOINT}/{person_id}", None)
    assert status == 200
    assert body["id"] == person_id


@pytest.mark.asyncio
async def test_non_existing_get_by_id(
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    persons_data = create_persons_es_data(1)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    person_id = uuid.uuid4()
    body, status = await make_get_request(f"{PERSONS_ENDPOINT}/{person_id}", None)
    assert status == 404


@pytest.mark.parametrize(
    "page_number, page_size, expected_items_count, expected_has_next, expected_has_prev",  # noqa E501
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
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
    page_number: int,
    page_size: int,
    expected_items_count: int,
    expected_has_next: bool,
    expected_has_prev: bool,
) -> None:
    persons_count = 60
    persons_data = create_persons_es_data(persons_count)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    params = {"page_number": page_number, "page_size": page_size}
    body, status = await make_get_request(PERSONS_ENDPOINT, params)
    assert status == 200

    assert len(body["items"]) == expected_items_count
    assert body["has_next"] is expected_has_next
    assert body["has_prev"] is expected_has_prev

    if expected_items_count > 0:
        last_item_index = page_number * page_size - 1
        assert body["items"][-1]["id"] == persons_data[last_item_index]["_source"]["id"]


@pytest.mark.asyncio
async def test_search(
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    persons_count = DEFAULT_PERSONS_COUNT
    persons_data = create_persons_es_data(persons_count)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    target_person = random.choice(persons_data)["_source"]
    search_query = target_person["full_name"]

    params = {"search": search_query}
    body, status = await make_get_request(PERSONS_ENDPOINT, params)

    assert status == 200

    found_ids = [item["id"] for item in body["items"]]
    assert target_person["id"] in found_ids


@pytest.mark.asyncio
async def test_person_movies_list(
    create_persons_es_data: CreatePersonsDataType,
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    persons_count = 1
    persons_data = create_persons_es_data(persons_count)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    person_in_movie = {
        "id": persons_data[0]["_source"]["id"],
        "name": persons_data[0]["_source"]["full_name"],
    }

    movies_count = 10
    movies_data = create_movies_es_data(movies_count, [person_in_movie], 1)
    await es_write_data(
        test_settings.elastic_movies_index_name,
        movies_data,
        test_settings.elastic_movies_index_mapping,
    )

    person_id = persons_data[0]["_source"]["id"]
    params = {"page_size": 10}
    body, status = await make_get_request(
        f"{PERSONS_ENDPOINT}/{person_id}/movies",
        params,
    )

    assert status == 200
    assert len(body["items"]) == movies_count


@pytest.mark.asyncio
async def test_cached_person_movies_list(
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    es_client: AsyncElasticsearch,
    make_get_request: MakeGetRequestType,
) -> None:
    async def check_person_movies(
        person_id: str,
        page_size: int,
        expected_status: int,
        detail: str | None = None,
    ) -> None:
        body, status = await make_get_request(
            f"{PERSONS_ENDPOINT}/{person_id}/movies",
            {"page_size": page_size},
        )
        assert status == expected_status
        if detail is not None:
            assert body["detail"] == detail

    persons_count = 10
    persons_data = create_persons_es_data(persons_count)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    person_id = persons_data[0]["_source"]["id"]
    page_size = 10

    # Запрос, данные кэшируются
    await check_person_movies(person_id, page_size, 200)
    await es_client.indices.delete(index=test_settings.elastic_persons_index_name)
    # Не попали в кэш
    await check_person_movies(
        person_id,
        page_size + 10,
        500,
        detail="Elastic index not found error",
    )
    # Так как индекс удален, получаем данные из кэша
    await check_person_movies(person_id, page_size, 200)


@pytest.mark.asyncio
async def test_person_movies_pagination(
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    persons_count = 10
    persons_data = create_persons_es_data(persons_count)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    person_id = persons_data[0]["_source"]["id"]
    params = {"page_number": 1, "page_size": 5}
    body, status = await make_get_request(
        f"{PERSONS_ENDPOINT}/{person_id}/movies",
        params,
    )

    assert status == 200
    assert len(body["items"]) <= 5
    assert body["page_number"] == 1


@pytest.mark.asyncio
async def test_non_existing_person_movies(
    create_persons_es_data: CreatePersonsDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    persons_count = 10
    persons_data = create_persons_es_data(persons_count)
    await es_write_data(
        test_settings.elastic_persons_index_name,
        persons_data,
        test_settings.elastic_persons_index_mapping,
    )

    person_id = uuid.uuid4()
    params = {"page_size": 10}
    body, status = await make_get_request(
        f"{PERSONS_ENDPOINT}/{person_id}/movies",
        params,
    )

    assert status == 404
