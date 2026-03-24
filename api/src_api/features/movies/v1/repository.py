import elasticsearch

from abc import ABC, abstractmethod
from typing import Annotated, Any
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
    async def get_list(
        self,
        page_number: int,
        page_size: int,
        sort: str | None,
        genre: str | None,
        search: str | None,
    ) -> list[MovieDTO]:
        pass


class MoviesElasticRepo(BaseMoviesRepo):
    SEARCH_FIELDS = [
        "actors_names",
        "writers_names",
        "title",
        "description",
        "genres",
    ]

    def __init__(self, index_name: str, client: AsyncElasticsearch) -> None:
        self.index_name = index_name
        self.client = client

    async def get_by_id(self, id: UUID) -> MovieDTO | None:
        try:
            result = await self.client.get(
                index=self.index_name,
                id=str(id),
            )
            return MovieDTO(**result.body["_source"])
        except elasticsearch.NotFoundError:
            return None

    async def get_list(
        self,
        page_number: int,
        page_size: int,
        sort: str | None,
        genre: str | None,
        search: str | None,
    ) -> list[MovieDTO]:
        from_ = (page_number - 1) * page_size

        body: dict[str, Any] = {
            "from": from_,
            "size": page_size,
        }
        if sort:
            body["sort"] = [
                {
                    sort.lstrip("-"): {
                        "order": "desc" if sort.startswith("-") else "asc",
                    },
                },
            ]

        if genre or search:
            body.setdefault("query", {"bool": {}})

            if genre:
                body["query"]["bool"]["filter"] = [
                    {"term": {"genres": genre}},
                ]

            if search:
                body["query"]["bool"]["must"] = [
                    {
                        "multi_match": {
                            "query": search,
                            "fuzziness": "auto",
                            "fields": self.SEARCH_FIELDS,
                        },
                    },
                ]

        result = await self.client.search(
            index=self.index_name,
            body=body,
        )
        return [MovieDTO(**movie["_source"]) for movie in result.body["hits"]["hits"]]


class MoviesRedisRepo(BaseMoviesRepo):
    pass


def get_movies_elastic_repo(
    client: Annotated[AsyncElasticsearch, Depends(get_elastic_client)],
) -> MoviesElasticRepo:
    return MoviesElasticRepo(
        settings.elastic_movies_index_name,
        client,
    )
