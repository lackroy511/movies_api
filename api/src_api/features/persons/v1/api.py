from uuid import UUID
from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from src_api.features.persons.v1.exceptions import PersonNotFoundError
from src_api.features.persons.v1.schemas import PersonResponse
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
    person_id: UUID,
    persons_service: Annotated[PersonsService, Depends(get_persons_service)],
) -> PersonResponse:
    try:
        person = await persons_service.get_by_id(person_id)
        return PersonResponse(**asdict(person))
    except PersonNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        ) from None
