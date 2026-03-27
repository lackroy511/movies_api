from uuid import UUID
from typing import Annotated, Any

import elasticsearch
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src_api.core.config.settings import settings
from src_api.core.db.elastic_db import get_elastic_client
from src_api.features.persons.v1.dto import PersonDTO, PersonsListDTO


class PersonsElasticRepo:
    SEARCH_FIELDS = ["full_name"]

    def __init__(self, index_name: str, client: AsyncElasticsearch) -> None:
        self.index_name = index_name
        self.client = client

    async def get_by_id(self, id: UUID) -> PersonDTO | None:
        try:
            result = await self.client.get(
                index=self.index_name,
                id=str(id),
            )
            return PersonDTO(**result.body["_source"])
        except elasticsearch.NotFoundError:
            return None

    async def get_list(
        self,
        page_number: int,
        page_size: int,
        search: str | None,
    ) -> PersonsListDTO:
        from_ = (page_number - 1) * page_size

        body: dict[str, Any] = {
            "from": from_,
            "size": page_size,
        }

        if search:
            body.setdefault("query", {"bool": {}})
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
        return PersonsListDTO(
            total=result.body["hits"]["total"]["value"],
            items=[
                PersonDTO(**person["_source"]) for person in result.body["hits"]["hits"]
            ],
        )


# Запрос на поиск фильмов по персоне
# {
#   "query": {
#     "bool": {
#       "should": [
#         {
#           "nested": {
#             "path": "directors",
#             "query": {
#               "term": { "directors.id": "PERSON_ID" }
#             }
#           }
#         },
#         {
#           "nested": {
#             "path": "actors",
#             "query": {
#               "term": { "actors.id": "PERSON_ID" }
#             }
#           }
#         },
#         {
#           "nested": {
#             "path": "writers",
#             "query": {
#               "term": { "writers.id": "PERSON_ID" }
#             }
#           }
#         }
#       ],
#       "minimum_should_match": 1
#     }
#   }
# }


def get_persons_elastic_repo(
    client: Annotated[AsyncElasticsearch, Depends(get_elastic_client)],
) -> PersonsElasticRepo:
    return PersonsElasticRepo(
        settings.elastic_persons_index_name,
        client,
    )
