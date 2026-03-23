from typing import Annotated
from uuid import UUID

from anyio.functools import lru_cache
from fastapi import Depends

from src_api.features.movies.v1.dto import Movie
from src_api.features.movies.v1.exceptions import MovieNotFoundError
from src_api.features.movies.v1.repository import (
    BaseMoviesRepo,
    MoviesElasticRepo,
    get_movies_elastic_repo,
)


class MoviesService:
    def __init__(self, repo: BaseMoviesRepo) -> None:
        self.repo = repo

    async def get_by_id(self, id: UUID) -> Movie:
        movie = await self.repo.get_by_id(id)
        if not movie:
            raise MovieNotFoundError("Movie not found")
        
        return movie

    async def get_by_filter(self) -> list[Movie]:
        return await self.repo.get_by_filter()


@lru_cache()
async def get_movies_service(
    elastic_repo: Annotated[MoviesElasticRepo, Depends(get_movies_elastic_repo)],
) -> MoviesService:
    return MoviesService(elastic_repo)
