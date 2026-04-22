from abc import ABC, abstractmethod
from typing import Annotated, Any

import elasticsearch
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src_api.core.config.settings import settings
from src_api.core.db.elastic_db import get_elastic_client
from src_api.features.persons.v1.dto import (
    PersonDetailDTO,
    PersonDTO,
    PersonMovieDTO,
    PersonMoviesListDTO,
    PersonsListDTO,
)


class PersonsRepoInterface(ABC):
    @abstractmethod
    async def get_by_id(self, id: str) -> PersonDetailDTO | None: ...

    @abstractmethod
    async def get_list(
        self,
        page_number: int,
        page_size: int,
        search: str | None,
    ) -> PersonsListDTO: ...

    @abstractmethod
    async def get_movies_by_person_id(
        self,
        person_id: str,
        page_number: int,
        page_size: int,
        sort: str | None,
    ) -> PersonMoviesListDTO: ...


class PersonsElasticRepo(PersonsRepoInterface):
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

    async def get_by_id(self, id: str) -> PersonDetailDTO | None:
        try:
            person = await self.client.get(
                index=self.index_name,
                id=str(id),
            )
            return PersonDetailDTO(
                id=person.body["_source"]["id"],
                full_name=person.body["_source"]["full_name"],
            )
        except elasticsearch.NotFoundError as e:
            if e.message == "index_not_found_exception":
                raise e

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
                    id=movie["_source"]["id"],
                    creation_date=movie["_source"]["creation_date"],
                    file_path=movie["_source"]["file_path"],
                    title=movie["_source"]["title"],
                    imdb_rating=movie["_source"]["imdb_rating"],
                    roles=[
                        role_name
                        for field_name, role_name in [
                            ("actors", "actor"),
                            ("directors", "director"),
                            ("writers", "writer"),
                        ]
                        if any(
                            entry.get("id") == person_id
                            for entry in movie["_source"].get(field_name, [])
                        )
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
