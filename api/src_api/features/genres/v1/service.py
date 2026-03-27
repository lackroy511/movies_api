from typing import Annotated, cast

from fastapi import Depends

from src_api.core.db.redis_db import (
    RedisCacheClient,
    get_redis_client,
)
from src_api.features.genres.v1.dto import Genre, GenresListDTO
from src_api.features.genres.v1.exceptions import GenreNotFoundError
from src_api.features.genres.v1.repository import (
    GenresElasticRepo,
    get_genres_elastic_repo,
)


class GenresService:
    def __init__(
        self,
        repo: GenresElasticRepo,
        cache_client: RedisCacheClient,
    ) -> None:
        self.repo = repo
        self.cache_client = cache_client
        self.cache_prefix = "genres"

    async def get_by_id(self, id: str) -> Genre:
        cache_key = self.cache_client.build_cache_key(self.cache_prefix, id)

        genre = await self.cache_client.get_cache(cache_key, Genre)
        if genre:
            return genre

        genre = await self.repo.get_by_id(id)
        if not genre:
            raise GenreNotFoundError("Genre not found")

        await self.cache_client.set_cache(cache_key, genre)
        return genre

    async def get_list(
        self,
        page_number: int,
        page_size: int,
        search: str | None,
    ) -> GenresListDTO:
        cache_key = self.cache_client.build_cache_key(
            self.cache_prefix,
            page_number,
            page_size,
            search,
        )

        genres = await self.cache_client.get_cache(cache_key, GenresListDTO)
        if genres:
            genres.items = [Genre(**cast(dict, genre)) for genre in genres.items]
            return genres
        
        genres = await self.repo.get_list(
            page_number=page_number,
            page_size=page_size,
            search=search,
        )
        await self.cache_client.set_cache(cache_key, genres)
        return genres


def get_genres_service(
    elastic_repo: Annotated[GenresElasticRepo, Depends(get_genres_elastic_repo)],
    redis_repo: Annotated[RedisCacheClient, Depends(get_redis_client)],
) -> GenresService:
    return GenresService(elastic_repo, redis_repo)