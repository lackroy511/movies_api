from dataclasses import asdict
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src_api.features.movies.v1.exceptions import MovieNotFoundError
from src_api.features.movies.v1.schemas import MovieResponse
from src_api.features.movies.v1.service import MoviesService, get_movies_service

router = APIRouter(prefix="/v1", tags=["V1 Фильмы"])

SortByType = Literal["imdb_rating", "-imdb_rating"]


@router.get("/movies")
async def get_movies_list(
    movies_service: Annotated[MoviesService, Depends(get_movies_service)],
    page_number: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    sort: SortByType | None = Query(None, description="Сортировка по полю"),  # noqa: B008
    genre: str | None = Query(None, description="Фильтр по названию жанра"),
) -> list[MovieResponse]:
    movies = await movies_service.get_list(page_number, page_size, sort, genre)
    return [MovieResponse(**asdict(movie)) for movie in movies]


@router.get("/movies/{movie_id:uuid}")
async def get_movie_by_id(
    movie_id: UUID,
    movies_service: Annotated[MoviesService, Depends(get_movies_service)],
) -> MovieResponse:
    try:
        movie = await movies_service.get_by_id(movie_id)
        return MovieResponse(**asdict(movie))
    except MovieNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Фильм не найден",
        ) from None
