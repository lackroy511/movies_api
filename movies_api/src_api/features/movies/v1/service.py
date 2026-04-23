from src_api.core.exc.exceptions import ForbiddenError
from src_api.core.config.settings import settings
from src_api.features.shared.types import RolesType
from datetime import date
from typing import Annotated, cast

from dateutil.relativedelta import relativedelta


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

    async def get_by_id(self, id: str, user_roles: list[RolesType]) -> MovieDTO:
        cache_key = self.cache_client.build_cache_key(self.cache_prefix, id)

        movie = await self.cache_client.get_cache(cache_key, MovieDTO)
        if movie:
            self._check_movie_access(movie, user_roles)
            return movie

        movie = await self.repo.get_by_id(id)
        if not movie:
            raise MovieNotFoundError("Movie not found")

        self._check_movie_access(movie, user_roles)
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

    def _check_movie_access(self, movie: MovieDTO, user_roles: list[RolesType]) -> None:
        if movie.creation_date:
            if (
                self._is_older(movie.creation_date, settings.non_subscriber_content_age)
                and settings.subscriber_role not in user_roles
            ):
                raise ForbiddenError("Access forbidden")

    def _is_older(self, movie_date: str, non_subscriber_content_age: int) -> bool:
        date_obj = date.fromisoformat(movie_date)
        three_years_ago = date.today() - relativedelta(
            years=settings.non_subscriber_content_age,
        )
        return date_obj > three_years_ago


def get_movies_service(
    elastic_repo: Annotated[MoviesElasticRepo, Depends(get_movies_elastic_repo)],
    redis_repo: Annotated[RedisCacheClient, Depends(get_redis_client)],
) -> MoviesService:
    return MoviesService(elastic_repo, redis_repo)
