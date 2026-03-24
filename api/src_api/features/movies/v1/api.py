from dataclasses import asdict
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src_api.features.movies.v1.exceptions import MovieNotFoundError
from src_api.features.movies.v1.schemas import MovieResponse
from src_api.features.movies.v1.service import MoviesService, get_movies_service

router = APIRouter(prefix="/v1", tags=["V1 Movies"])


@router.get("/movies")
async def get_movies_list(
    movies_service: Annotated[MoviesService, Depends(get_movies_service)],
) -> list[MovieResponse]:
    movies = await movies_service.get_by_filter()
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
