from uuid import UUID
from typing import Annotated, Any

import elasticsearch
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src_api.core.config.settings import settings
from src_api.core.db.elastic_db import get_elastic_client
from src_api.features.genres.v1.dto import Genre, GenresListDTO


class GenresElasticRepo:
    SEARCH_FIELDS = [
        "name",
        "description",
    ]

    def __init__(self, index_name: str, client: AsyncElasticsearch) -> None:
        self.index_name = index_name
        self.client = client

    async def get_by_id(self, id: UUID) -> Genre | None:
        try:
            result = await self.client.get(
                index=self.index_name,
                id=str(id),
            )
            return Genre(**result.body["_source"])
        except elasticsearch.NotFoundError:
            return None

    async def get_list(
        self,
        page_number: int,
        page_size: int,
        search: str | None,
    ) -> GenresListDTO:
        from_ = (page_number - 1) * page_size

        body: dict[str, Any] = {
            "from": from_,
            "size": page_size,
        }

        if search:
            body["query"] = {
                "multi_match": {
                    "query": search,
                    "fuzziness": "auto",
                    "fields": self.SEARCH_FIELDS,
                },
            }

        result = await self.client.search(
            index=self.index_name,
            body=body,
        )
        return GenresListDTO(
            total=result.body["hits"]["total"]["value"],
            items=[
                Genre(**genre["_source"]) for genre in result.body["hits"]["hits"]
            ],
        )


def get_genres_elastic_repo(
    client: Annotated[AsyncElasticsearch, Depends(get_elastic_client)],
) -> GenresElasticRepo:
    return GenresElasticRepo(
        settings.elastic_genres_index_name,
        client,
    )