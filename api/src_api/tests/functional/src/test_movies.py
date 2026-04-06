import uuid
import random
import pytest
from elasticsearch import AsyncElasticsearch

from src_api.tests.functional.conftest import (
    CreateMoviesDataType,
    EsWriteDataType,
    MakeGetRequestType,
)
from src_api.tests.functional.settings import test_settings


MOVIES_ENDPOINT = "/api/v1/movies"
DEFAULT_MOVIES_COUNT = 60


@pytest.mark.asyncio
async def test_default_list(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_count = DEFAULT_MOVIES_COUNT
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    params = {"page_size": 10}
    body, status = await make_get_request(MOVIES_ENDPOINT, params)

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
            MOVIES_ENDPOINT,
            {"page_size": page_size},
        )
        assert status == expected_status
        if expected_total is not None:
            assert body["total"] == expected_total
        if detail is not None:
            assert body["detail"] == detail

    movies_count = DEFAULT_MOVIES_COUNT
    page_size = 10
    await es_write_data(
        test_settings.elastic_movies_index_name,
        create_movies_es_data(movies_count),
    )
    # Запрос, данные кэшируются
    await check_movies(page_size, 200, expected_total=movies_count)
    await es_client.indices.delete(index=test_settings.elastic_movies_index_name)
    # Не попали в кэш, убедились что индекс не существует
    await check_movies(page_size + 10, 500, detail="Elastic index not found error")
    # Так как индекс удален, получаем данные, но они из кэша
    await check_movies(page_size, 200, expected_total=movies_count)


@pytest.mark.asyncio
async def test_get_by_id(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_data = create_movies_es_data(1)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    movie_id = movies_data[0]["_source"]["id"]
    body, status = await make_get_request(f"{MOVIES_ENDPOINT}/{movie_id}", None)

    assert status == 200
    assert body["id"] == movie_id
    assert body["title"] == movies_data[0]["_source"]["title"]


@pytest.mark.asyncio
async def test_cached_get_by_id(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    es_client: AsyncElasticsearch,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_data = create_movies_es_data(1)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    movie_id = movies_data[0]["_source"]["id"]

    body, status = await make_get_request(f"{MOVIES_ENDPOINT}/{movie_id}", None)
    assert status == 200
    assert body["id"] == movie_id

    await es_client.indices.delete(index=test_settings.elastic_movies_index_name)

    body, status = await make_get_request(f"{MOVIES_ENDPOINT}/{movie_id}", None)
    assert status == 200
    assert body["id"] == movie_id


@pytest.mark.asyncio
async def test_non_existing_get_by_id(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_data = create_movies_es_data(1)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    movie_id = uuid.uuid4()
    body, status = await make_get_request(f"{MOVIES_ENDPOINT}/{movie_id}", None)
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
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
    page_number: int,
    page_size: int,
    expected_items_count: int,
    expected_has_next: bool,
    expected_has_prev: bool,
) -> None:
    movies_count = 60
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    params = {"page_number": page_number, "page_size": page_size}
    body, status = await make_get_request(MOVIES_ENDPOINT, params)
    assert status == 200

    assert len(body["items"]) == expected_items_count
    assert body["has_next"] is expected_has_next
    assert body["has_prev"] is expected_has_prev

    if expected_items_count > 0:
        last_item_index = page_number * page_size - 1
        assert body["items"][-1]["id"] == movies_data[last_item_index]["_source"]["id"]


@pytest.mark.parametrize(
    "sort_field",
    [
        ("imdb_rating"),
        ("-imdb_rating"),
    ],
)
@pytest.mark.asyncio
async def test_sorting_movies_by_rating(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
    sort_field: str,
) -> None:
    movies_count = DEFAULT_MOVIES_COUNT
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    if sort_field.startswith("-"):
        expected_first_item_rating = max(
            movies_data,
            key=lambda x: x["_source"]["imdb_rating"],
        )["_source"]["imdb_rating"]
    else:
        expected_first_item_rating = min(
            movies_data,
            key=lambda x: x["_source"]["imdb_rating"],
        )["_source"]["imdb_rating"]

    params = {"sort": sort_field}
    body, status = await make_get_request(MOVIES_ENDPOINT, params)
    assert status == 200
    assert body["items"][0]["imdb_rating"] == expected_first_item_rating


@pytest.mark.asyncio
async def test_sorting_unexpected_field(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_count = DEFAULT_MOVIES_COUNT
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    params = {"sort": "unexpected_field"}
    body, status = await make_get_request(MOVIES_ENDPOINT, params)
    assert status == 422


@pytest.mark.asyncio
async def test_filter_by_genre(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
    test_genre_names: list[str],
) -> None:
    movies_count = DEFAULT_MOVIES_COUNT
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    genre = test_genre_names[0]
    expected_count = len([m for m in movies_data if genre in m["_source"]["genres"]])

    params = {"genre": genre}
    body, status = await make_get_request(MOVIES_ENDPOINT, params)

    assert status == 200
    assert body["total"] == expected_count
    for movie in body["items"]:
        assert genre in movie["genres"]


@pytest.mark.asyncio
async def test_filter_by_non_existing_genre(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_count = DEFAULT_MOVIES_COUNT
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    genre = "NonExistingGenre"

    params = {"genre": genre}
    body, status = await make_get_request(MOVIES_ENDPOINT, params)

    assert status == 200
    assert body["total"] == 0


@pytest.mark.asyncio
async def test_search_by_title(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_count = DEFAULT_MOVIES_COUNT
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    target_movie = random.choice(movies_data)["_source"]
    search_query = target_movie["title"]

    params = {"search": search_query}
    body, status = await make_get_request(MOVIES_ENDPOINT, params)

    assert status == 200
    assert body["items"][0]["id"] == target_movie["id"]


@pytest.mark.asyncio
async def test_search_by_description(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_count = DEFAULT_MOVIES_COUNT
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    target_movie = random.choice(movies_data)["_source"]
    description = target_movie["description"]
    search_query = description[: len(description) // 3]

    params = {"search": search_query}
    body, status = await make_get_request(MOVIES_ENDPOINT, params)

    assert status == 200
    assert body["items"][0]["id"] == target_movie["id"]


@pytest.mark.asyncio
async def test_search_by_person(
    create_movies_es_data: CreateMoviesDataType,
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    movies_count = DEFAULT_MOVIES_COUNT
    movies_data = create_movies_es_data(movies_count)
    await es_write_data(test_settings.elastic_movies_index_name, movies_data)

    target_movie = random.choice(movies_data)["_source"]
    role_keys = ["directors_names", "actors_names", "writers_names"]
    chosen_role = random.choice(role_keys)
    
    random_person = random.choice(target_movie[chosen_role])

    params = {"search": random_person}
    body, status = await make_get_request(MOVIES_ENDPOINT, params)

    assert status == 200
    assert len(body["items"]) > 0
    
    assert any(
        random_person in body["items"][0].get(role, []) 
        for role in role_keys
    )
