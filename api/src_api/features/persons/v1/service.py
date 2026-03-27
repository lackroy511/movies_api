from typing import Annotated, cast

from fastapi import Depends

from src_api.core.db.redis_db import (
    RedisCacheClient,
    get_redis_client,
)
from src_api.features.persons.v1.dto import (
    PersonDTO,
    PersonsListDTO,
    PersonMoviesListDTO,
    PersonMovieDTO,
)
from src_api.features.persons.v1.exceptions import PersonNotFoundError
from src_api.features.persons.v1.repository import (
    PersonsElasticRepo,
    get_persons_elastic_repo,
)


class PersonsService:
    def __init__(
        self,
        repo: PersonsElasticRepo,
        cache_client: RedisCacheClient,
    ) -> None:
        self.repo = repo
        self.cache_client = cache_client
        self.cache_prefix = "persons"

    async def get_by_id(self, id: str) -> PersonDTO:
        cache_key = self.cache_client.build_cache_key(self.cache_prefix, id)

        person = await self.cache_client.get_cache(cache_key, PersonDTO)
        if person:
            return person

        person = await self.repo.get_by_id(id)
        if not person:
            raise PersonNotFoundError("Person not found")

        await self.cache_client.set_cache(cache_key, person)
        return person

    async def get_list(
        self,
        page_number: int,
        page_size: int,
        search: str | None,
    ) -> PersonsListDTO:
        cache_key = self.cache_client.build_cache_key(
            self.cache_prefix,
            page_number,
            page_size,
            search,
        )

        persons = await self.cache_client.get_cache(cache_key, PersonsListDTO)
        if persons:
            persons.items = [
                PersonDTO(**cast(dict, person)) for person in persons.items
            ]
            return persons

        persons = await self.repo.get_list(
            page_number=page_number,
            page_size=page_size,
            search=search,
        )
        await self.cache_client.set_cache(cache_key, persons)
        return persons

    async def get_movies_by_person_id(
        self,
        person_id: str,
        page_number: int,
        page_size: int,
        sort: str | None,
    ) -> PersonMoviesListDTO:
        cache_key = self.cache_client.build_cache_key(
            self.cache_prefix,
            person_id,
            page_number,
            page_size,
            sort,
        )
        person_movies = await self.cache_client.get_cache(
            cache_key,
            PersonMoviesListDTO,
        )
        if person_movies:
            person_movies.items = [
                PersonMovieDTO(**cast(dict, person_movie))
                for person_movie in person_movies.items
            ]
            return person_movies

        person = await self.repo.get_by_id(person_id)
        if not person:
            raise PersonNotFoundError("Person not found")
        person_movies = await self.repo.get_movies_by_person_id(
            person_id=person_id,
            person_full_name=person.full_name,
            page_number=page_number,
            page_size=page_size,
            sort=sort,
        )
        await self.cache_client.set_cache(cache_key, person_movies)
        return person_movies


def get_persons_service(
    elastic_repo: Annotated[PersonsElasticRepo, Depends(get_persons_elastic_repo)],
    redis_repo: Annotated[RedisCacheClient, Depends(get_redis_client)],
) -> PersonsService:
    return PersonsService(elastic_repo, redis_repo)
