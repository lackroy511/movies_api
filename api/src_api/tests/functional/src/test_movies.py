import asyncio

import pytest
from elasticsearch import AsyncElasticsearch

from src_api.tests.functional.conftest import (
    CreateMoviesDataType,
    EsWriteDataType,
    MakeGetRequestType,
)
from src_api.tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_default_list(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_count = 60
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    params = {"page_size": 10}
    body, status = await make_get_request("/api/v1/movies", params)

    assert status == 200
    assert body["total"] == movies_count
    assert body["page_number"] == 1
    assert body["has_next"] is True
    assert body["has_prev"] is False


@pytest.mark.asyncio
async def test_cached_list(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    es_client: AsyncElasticsearch,
    make_get_request: MakeGetRequestType,
) -> None:
    async def check_movies(
        page_size: int,
        expected_status: int,
        expected_total: int | None = None,
        detail: str | None = None,
    ) -> None:
        body, status = await make_get_request(
            "/api/v1/movies",
            {"page_size": page_size},
        )
        assert status == expected_status
        if expected_total is not None:
            assert body["total"] == expected_total
        if detail is not None:
            assert body["detail"] == detail

    async def delete_index() -> None:
        await es_client.indices.delete(
            index=test_settings.elastic_movies_index_name,
        )
        while await es_client.indices.exists(
            index=test_settings.elastic_movies_index_name,
        ):
            await asyncio.sleep(0.1)

    movies_count = 60
    page_size = 10
    await es_write_data(
        test_settings.elastic_movies_index_name,
        create_movies_es_data(movies_count),
    )
    # Создали кэш
    await check_movies(page_size, 200, expected_total=movies_count)
    await delete_index()
    # Не попали в кэш, убедились что индекс не существует
    await check_movies(page_size + 10, 500, detail="Elastic index not found error")
    # Так как индекс удален, получаем данные, но они из кэша
    await check_movies(page_size, 200, expected_total=movies_count)
