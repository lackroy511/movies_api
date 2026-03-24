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
    page_number: int = Query(1, ge=1, description="Movies page number"),
    page_size: int = Query(20, ge=1, le=100, description="Movies page size"),
    sort: SortByType | None = Query(None, description="Sort by field"),  # noqa: B008
    genre: str | None = Query(None, description="Filter by genre name"),
    search: str | None = Query(None, description="Full text search"),
) -> list[MovieResponse]:
    movies = await movies_service.get_list(
        page_number,
        page_size,
        sort,
        genre.strip() if genre else None,
        search.strip() if search else None,
    )
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
            detail="Movie not found",
        ) from None
