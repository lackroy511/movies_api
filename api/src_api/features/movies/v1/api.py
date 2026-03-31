from src_api.features.shared.query_params import PaginationParams
from dataclasses import asdict
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src_api.features.movies.v1.exceptions import ErrorMessages, MovieNotFoundError
from src_api.features.movies.v1.schemas import MovieResponse
from src_api.features.movies.v1.service import MoviesService, get_movies_service
from src_api.features.shared.schemas import PaginatedResponse
from src_api.features.shared.types import SortMoviesType

router = APIRouter(prefix="/v1", tags=["V1 Movies"])


@router.get("/movies")
async def get_movies_list(
    movies_service: Annotated[MoviesService, Depends(get_movies_service)],
    pagination: Annotated[PaginationParams, Depends(PaginationParams)],
    sort: SortMoviesType | None = Query(None, description="Sort by field"),  # noqa: B008
    genre: str | None = Query(None, description="Filter by genre name"),
    search: str | None = Query(None, description="Full text search"),
) -> PaginatedResponse[MovieResponse]:
    movies = await movies_service.get_list(
        pagination.page_number,
        pagination.page_size,
        sort,
        genre.strip() if genre else None,
        search.strip() if search else None,
    )
    return PaginatedResponse[MovieResponse](
        total=movies.total,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        has_next=True
        if pagination.page_number * pagination.page_size < movies.total
        else False,
        has_prev=True
        if pagination.page_number > 1 and pagination.page_number <= movies.total
        else False,
        items=[MovieResponse(**asdict(movie)) for movie in movies.items],
    )


@router.get(
    "/movies/{movie_id:uuid}",
    responses={
        404: {
            "description": ErrorMessages.MOVIE_NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {"detail": ErrorMessages.MOVIE_NOT_FOUND},
                },
            },
        },
    },
)
async def get_movie_by_id(
    movie_id: UUID,
    movies_service: Annotated[MoviesService, Depends(get_movies_service)],
) -> MovieResponse:
    try:
        movie = await movies_service.get_by_id(str(movie_id))
        return MovieResponse(**asdict(movie))
    except MovieNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        ) from None
