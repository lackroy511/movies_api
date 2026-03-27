from uuid import UUID
from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src_api.features.genres.v1.exceptions import GenreNotFoundError
from src_api.features.genres.v1.schemas import GenreResponse
from src_api.features.genres.v1.service import GenresService, get_genres_service
from src_api.features.shared.schemas import PaginatedResponse

router = APIRouter(prefix="/v1", tags=["V1 Genres"])


@router.get("/genres")
async def get_genres_list(
    genres_service: Annotated[GenresService, Depends(get_genres_service)],
    page_number: int = Query(1, ge=1, description="Genres page number"),
    page_size: int = Query(20, ge=1, le=100, description="Genres page size"),
    search: str | None = Query(None, description="Full text search"),
) -> PaginatedResponse[GenreResponse]:
    genres = await genres_service.get_list(
        page_number,
        page_size,
        search.strip() if search else None,
    )
    return PaginatedResponse[GenreResponse](
        total=genres.total,
        page_number=page_number,
        page_size=page_size,
        has_next=True if page_number * page_size < genres.total else False,
        has_prev=True if page_number > 1 and page_number <= genres.total else False,
        items=[GenreResponse(**asdict(genre)) for genre in genres.items],
    )


@router.get("/genres/{genre_id:uuid}")
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