from typing import Annotated, Any

import elasticsearch
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src_api.core.config.settings import settings
from src_api.core.db.elastic_db import get_elastic_client
from src_api.features.persons.v1.dto import (
    PersonDTO,
    PersonsListDTO,
    PersonMoviesListDTO,
    PersonMovieDTO,
)


class PersonsElasticRepo:
    SEARCH_FIELDS = ["full_name"]

    def __init__(
        self,
        index_name: str,
        movies_index_name: str,
        client: AsyncElasticsearch,
    ) -> None:
        self.index_name = index_name
        self.movies_index_name = movies_index_name
        self.client = client

    async def get_by_id(self, id: str) -> PersonDTO | None:
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

    async def get_movies_by_person_id(
        self,
        person_id: str,
        person_full_name: str,
        page_number: int,
        page_size: int,
        sort: str | None,
    ) -> PersonMoviesListDTO:
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
        body["query"] = {
            "bool": {
                "should": [
                    {
                        "nested": {
                            "path": "directors",
                            "query": {"term": {"directors.id": person_id}},
                        },
                    },
                    {
                        "nested": {
                            "path": "actors",
                            "query": {"term": {"actors.id": person_id}},
                        },
                    },
                    {
                        "nested": {
                            "path": "writers",
                            "query": {"term": {"writers.id": person_id}},
                        },
                    },
                ],
                "minimum_should_match": 1,
            },
        }

        result = await self.client.search(
            index=self.movies_index_name,
            body=body,
        )
        return PersonMoviesListDTO(
            total=result.body["hits"]["total"]["value"],
            items=[
                PersonMovieDTO(
                    person_id=str(person_id),
                    person_full_name=person_full_name,
                    movie_id=movie["_source"]["id"],
                    movie_title=movie["_source"]["title"],
                    description=movie["_source"]["description"],
                    imdb_rating=movie["_source"]["imdb_rating"],
                    roles=[
                        role
                        for role, field in [
                            ("actor", "actors_names"),
                            ("director", "directors_names"),
                            ("writer", "writers_names"),
                        ]
                        if person_full_name in movie["_source"][field]
                    ],
                )
                for movie in result.body["hits"]["hits"]
            ],
        )


def get_persons_elastic_repo(
    client: Annotated[AsyncElasticsearch, Depends(get_elastic_client)],
) -> PersonsElasticRepo:
    return PersonsElasticRepo(
        settings.elastic_persons_index_name,
        settings.elastic_movies_index_name,
        client,
    )
