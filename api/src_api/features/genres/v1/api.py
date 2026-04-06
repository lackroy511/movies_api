from dataclasses import asdict
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src_api.features.genres.v1.exceptions import ErrorMessages, GenreNotFoundError
from src_api.features.genres.v1.schemas import GenreResponse
from src_api.features.genres.v1.service import GenresService, get_genres_service
from src_api.features.shared.query_params import PaginationParams
from src_api.features.shared.schemas import PaginatedResponse

router = APIRouter(prefix="/v1", tags=["V1 Genres"])


@router.get("/genres")
async def get_genres_list(
    genres_service: Annotated[GenresService, Depends(get_genres_service)],
    pagination: Annotated[PaginationParams, Depends(PaginationParams)],
    search: str | None = Query(None, description="Full text search"),
) -> PaginatedResponse[GenreResponse]:
    genres = await genres_service.get_list(
        pagination.page_number,
        pagination.page_size,
        search.strip() if search else None,
    )
    return PaginatedResponse.from_list(
        total=genres.total,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        items=[GenreResponse(**asdict(genre)) for genre in genres.items],
    )


@router.get(
    "/genres/{genre_id:uuid}",
    responses={
        404: {
            "description": ErrorMessages.GENRE_NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {"detail": ErrorMessages.GENRE_NOT_FOUND},
                },
            },
        },
    },
)
async def get_genre_by_id(
    genre_id: UUID,
    genres_service: Annotated[GenresService, Depends(get_genres_service)],
) -> GenreResponse:
    try:
        genre = await genres_service.get_by_id(str(genre_id))
        return GenreResponse(**asdict(genre))
    except GenreNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Genre not found",
        ) from None
