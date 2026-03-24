from functools import lru_cache
from typing import Annotated
from uuid import UUID


from fastapi import Depends

from src_api.features.movies.v1.dto import MovieDTO
from src_api.features.movies.v1.exceptions import MovieNotFoundError
from src_api.features.movies.v1.repository import (
    BaseMoviesRepo,
    MoviesElasticRepo,
    get_movies_elastic_repo,
)


class MoviesService:
    def __init__(self, repo: BaseMoviesRepo) -> None:
        self.repo = repo

    async def get_by_id(self, id: UUID) -> MovieDTO:
        movie = await self.repo.get_by_id(id)
        if not movie:
            raise MovieNotFoundError("Movie not found")

        return movie

    async def get_list(
        self,
        page_number: int,
        page_size: int,
        sort: str | None,
        genre: str | None,
    ) -> list[MovieDTO]:
        return await self.repo.get_list(
            page_number=page_number,
            page_size=page_size,
            sort=sort,
            genre=genre,
        )


@lru_cache()
def get_movies_service(
    elastic_repo: Annotated[MoviesElasticRepo, Depends(get_movies_elastic_repo)],
) -> MoviesService:
    return MoviesService(elastic_repo)
