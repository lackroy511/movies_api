from elasticsearch import AsyncElasticsearch

from src_api.core.config.settings import settings

client = AsyncElasticsearch(
    hosts=[settings.elastic_base_url],
)


async def get_elastic_client() -> AsyncElasticsearch:
    return client