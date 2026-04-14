from dataclasses import asdict
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from src_api.features.persons.v1.exceptions import ErrorMessages, PersonNotFoundError
from src_api.features.persons.v1.schemas import (
    PersonDetailResponse,
    PersonMovieResponse,
    PersonResponse,
)
from src_api.features.persons.v1.service import PersonsService, get_persons_service
from src_api.features.shared.query_params import PaginationParams
from src_api.features.shared.schemas import PaginatedResponse
from src_api.features.shared.types import SortMoviesType

router = APIRouter(prefix="/v1", tags=["V1 Persons"])


@router.get("/persons")
async def get_persons_list(
    persons_service: Annotated[PersonsService, Depends(get_persons_service)],
    pagination: Annotated[PaginationParams, Depends(PaginationParams)],
    search: str | None = Query(None, description="Full text search"),
) -> PaginatedResponse[PersonResponse]:
    persons = await persons_service.get_list(
        pagination.page_number,
        pagination.page_size,
        search.strip() if search else None,
    )
    return PaginatedResponse.from_list(
        total=persons.total,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        items=[PersonResponse(**asdict(person)) for person in persons.items],
    )


@router.get(
    "/persons/{person_id:uuid}",
    responses={
        404: {
            "description": ErrorMessages.PERSON_NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {"detail": ErrorMessages.PERSON_NOT_FOUND},
                },
            },
        },
    },
)
async def get_person_by_id(
    persons_service: Annotated[PersonsService, Depends(get_persons_service)],
    person_id: UUID,
) -> PersonDetailResponse:
    try:
        person = await persons_service.get_by_id(str(person_id))
        return PersonDetailResponse(**asdict(person))
    except PersonNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        ) from None


@router.get(
    "/persons/{person_id:uuid}/movies",
    responses={
        404: {
            "description": ErrorMessages.PERSON_NOT_FOUND,
            "content": {
                "application/json": {
                    "example": {"detail": ErrorMessages.PERSON_NOT_FOUND},
                },
            },
        },
    },
)
async def get_person_movies(
    persons_service: Annotated[PersonsService, Depends(get_persons_service)],
    person_id: UUID,
    pagination: Annotated[PaginationParams, Depends(PaginationParams)],
    sort: SortMoviesType | None = Query(None, description="Sort by field"),  # noqa: B008
) -> PaginatedResponse[PersonMovieResponse]:
    try:
        person_movies = await persons_service.get_movies_by_person_id(
            person_id=str(person_id),
            page_number=pagination.page_number,
            page_size=pagination.page_size,
            sort=sort,
        )
        return PaginatedResponse.from_list(
            total=person_movies.total,
            page_number=pagination.page_number,
            page_size=pagination.page_size,
            items=[
                PersonMovieResponse(**asdict(person_movie))
                for person_movie in person_movies.items
            ],
        )
    except PersonNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=ErrorMessages.PERSON_NOT_FOUND,
        ) from None
