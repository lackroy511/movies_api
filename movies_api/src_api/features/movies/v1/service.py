from typing import Annotated, cast

from fastapi import Depends

from src_api.core.db.cache import (
    CacheClientInterface,
    RedisCacheClient,
    get_redis_client,
)
from src_api.features.movies.v1.dto import MovieDTO, MoviesListDTO
from src_api.features.movies.v1.exceptions import MovieNotFoundError
from src_api.features.movies.v1.repository import (
    MoviesElasticRepo,
    MoviesRepoInterface,
    get_movies_elastic_repo,
)


class MoviesService:
    def __init__(
        self,
        repo: MoviesRepoInterface,
        cache_client: CacheClientInterface,
    ) -> None:
        self.repo = repo
        self.cache_client = cache_client
        self.cache_prefix = "movies"

    async def get_by_id(self, id: str) -> MovieDTO:
        cache_key = self.cache_client.build_cache_key(self.cache_prefix, id)

        movie = await self.cache_client.get_cache(cache_key, MovieDTO)
        if movie:
            return movie

        movie = await self.repo.get_by_id(id)
        if not movie:
            raise MovieNotFoundError("Movie not found")

        await self.cache_client.set_cache(cache_key, movie)
        return movie

    async def get_list(
        self,
        page_number: int,
        page_size: int,
        sort: str | None,
        genre: str | None,
        search: str | None,
    ) -> MoviesListDTO:
        cache_key = self.cache_client.build_cache_key(
            self.cache_prefix,
            page_number,
            page_size,
            sort,
            genre,
            search,
        )

        movies = await self.cache_client.get_cache(cache_key, MoviesListDTO)
        if movies:
            movies.items = [MovieDTO(**cast(dict, movie)) for movie in movies.items]
            return movies

        movies = await self.repo.get_list(
            page_number=page_number,
            page_size=page_size,
            sort=sort,
            genre=genre,
            search=search,
        )
        await self.cache_client.set_cache(cache_key, movies)
        return movies


def get_movies_service(
    elastic_repo: Annotated[MoviesElasticRepo, Depends(get_movies_elastic_repo)],
    redis_repo: Annotated[RedisCacheClient, Depends(get_redis_client)],
) -> MoviesService:
    return MoviesService(elastic_repo, redis_repo)
