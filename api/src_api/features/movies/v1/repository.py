from abc import ABC, abstractmethod
from typing import Annotated
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src_api.core.config.settings import settings
from src_api.core.db.elastic_db import get_elastic_client
from src_api.features.movies.v1.dto import MovieDTO


class BaseMoviesRepo(ABC):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> MovieDTO | None:
        pass

    @abstractmethod
    async def get_by_filter(self) -> list[MovieDTO]:
        pass


class MoviesElasticRepo(BaseMoviesRepo):
    def __init__(self, index_name: str, client: AsyncElasticsearch) -> None:
        self.index_name = index_name
        self.client = client

    async def get_by_id(self, id: UUID) -> MovieDTO | None:
        result = await self.client.search(
            index=self.index_name,
            query={
                "term": {
                    "id": {"value": id},
                },
            },
        )
        if result.body["hits"]["hits"]:
            return MovieDTO(**result["hits"]["hits"][0]["_source"])

        return None

    async def get_by_filter(self) -> list[MovieDTO]:
        result = await self.client.search(
            index=self.index_name,
        )
        return [MovieDTO(**movie["_source"]) for movie in result.body["hits"]["hits"]]


class MoviesRedisRepo(BaseMoviesRepo):
    pass


async def get_movies_elastic_repo(
    client: Annotated[AsyncElasticsearch, Depends(get_elastic_client)],
) -> MoviesElasticRepo:
    return MoviesElasticRepo(
        settings.elastic_movies_index_name,
        client,
    )
