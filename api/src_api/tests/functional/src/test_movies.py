import pytest

from src_api.tests.functional.conftest import EsWriteDataType, MakeGetRequestType
from src_api.tests.functional.settings import test_settings


@pytest.mark.asyncio
async def test_search(
    movies_es_data: list[dict],
    es_write_data: EsWriteDataType,
    make_get_request: MakeGetRequestType,
) -> None:
    await es_write_data(test_settings.elastic_movies_index_name, movies_es_data)
    body, status = await make_get_request("/api/v1/movies", None)

    assert status == 200
    assert body["total"] == 60
