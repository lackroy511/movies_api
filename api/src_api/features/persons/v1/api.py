from src_api.features.shared.types import SortMoviesType
from uuid import UUID
from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src_api.features.persons.v1.exceptions import PersonNotFoundError
from src_api.features.persons.v1.schemas import PersonResponse, PersonMovieResponse
from src_api.features.persons.v1.service import PersonsService, get_persons_service
from src_api.features.shared.schemas import PaginatedResponse

router = APIRouter(prefix="/v1", tags=["V1 Persons"])


@router.get("/persons")
async def get_persons_list(
    persons_service: Annotated[PersonsService, Depends(get_persons_service)],
    page_number: int = Query(1, ge=1, description="Persons page number"),
    page_size: int = Query(20, ge=1, le=100, description="Persons page size"),
    search: str | None = Query(None, description="Full text search"),
) -> PaginatedResponse[PersonResponse]:
    persons = await persons_service.get_list(
        page_number,
        page_size,
        search.strip() if search else None,
    )
    return PaginatedResponse[PersonResponse](
        total=persons.total,
        page_number=page_number,
        page_size=page_size,
        has_next=True if page_number * page_size < persons.total else False,
        has_prev=True if page_number > 1 and page_number <= persons.total else False,
        items=[PersonResponse(**asdict(person)) for person in persons.items],
    )


@router.get("/persons/{person_id}")
async def get_person_by_id(
    persons_service: Annotated[PersonsService, Depends(get_persons_service)],
    person_id: UUID,
) -> PersonResponse:
    try:
        person = await persons_service.get_by_id(person_id)
        return PersonResponse(**asdict(person))
    except PersonNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        ) from None


@router.get("/persons/{person_id:uuid}/movies")
async def get_person_movies(
    persons_service: Annotated[PersonsService, Depends(get_persons_service)],
    person_id: UUID,
    page_number: int = Query(1, ge=1, description="Person movies page number"),
    page_size: int = Query(20, ge=1, le=100, description="Person movies page size"),
    sort: SortMoviesType | None = Query(None, description="Sort by field"),  # noqa: B008
) -> PaginatedResponse[PersonMovieResponse]:
    try:
        person_movies = await persons_service.get_movies_by_person_id(
            person_id=person_id,
            page_number=page_number,
            page_size=page_size,
            sort=sort,
        )
        return PaginatedResponse(
            total=person_movies.total,
            page_number=page_number,
            page_size=page_size,
            has_next=True if page_number * page_size < person_movies.total else False,
            has_prev=(
                True
                if page_number > 1 and page_number <= person_movies.total
                else False
            ),
            items=[
                PersonMovieResponse(
                    id=person_movie.id,
                    title=person_movie.title,
                    imdb_rating=person_movie.imdb_rating,
                )
                for person_movie in person_movies.items
            ],
        )
    except PersonNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        ) from None
