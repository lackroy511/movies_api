from abc import ABC, abstractmethod
from typing import Annotated, Any
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src_api.core.config.settings import settings
from src_api.core.db.elastic_db import get_elastic_client
from src_api.features.movies.v1.dto import Movie


class BaseMoviesRepo(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Movie | None:
        pass

    @abstractmethod
    async def get_by_filter(self, *args: Any, **kwargs: Any) -> list[Movie]:  # noqa: ANN401
        pass


class MoviesElasticRepo(BaseMoviesRepo):
    def __init__(self, index_name: str, client: AsyncElasticsearch) -> None:
        self.index_name = index_name
        self.client = client

    async def get_by_id(self, id: UUID) -> Movie | None:
        result = await self.client.search(
            index=self.index_name,
            query={
                "term": {
                    "id": {"value": id},
                },
            },
        )
        if result.body["hits"]["hits"]:
            return Movie(**result["hits"]["hits"][0]["_source"])
        
        return None

    async def get_by_filter(self) -> list[Movie]:
        return [Movie(**{})]


class MoviesRedisRepo(BaseMoviesRepo):
    pass


async def get_movies_elastic_repo(
    client: Annotated[AsyncElasticsearch, Depends(get_elastic_client)],
) -> MoviesElasticRepo:
    return MoviesElasticRepo(
        settings.elastic_movies_index_name,
        client,
    )
