from typing import Any

from elastic_transport import (
    ConnectionError,
    ConnectionTimeout,
    ObjectApiResponse,
    TlsError,
)
from elasticsearch import AsyncElasticsearch

from src_api.core.config.settings import settings
from src_api.utils.backoff import Backoff

RETRY_EXCEPTIONS = (
    ConnectionError,
    ConnectionTimeout,
    TlsError,
)


class BackoffAsyncElasticsearch(AsyncElasticsearch):
    @Backoff(RETRY_EXCEPTIONS)
    async def get(self, *args: Any, **kwargs: Any) -> ObjectApiResponse:  # noqa: ANN401
        return await super().get(*args, **kwargs)

    @Backoff(RETRY_EXCEPTIONS)
    async def search(self, *args: Any, **kwargs: Any) -> ObjectApiResponse:  # noqa: ANN401
        return await super().search(*args, **kwargs)


client = BackoffAsyncElasticsearch(
    hosts=[settings.elastic_base_url],
)


def get_elastic_client() -> AsyncElasticsearch:
    return client
