from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int = Field(description="Total number of items")
    page_number: int = Field(description="Page number")
    page_size: int = Field(description="Page size")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")
    items: list[T] = Field(description="List of items")

    @classmethod
    def from_list(
        cls,
        total: int,
        page_number: int,
        page_size: int,
        items: list[T],
    ) -> PaginatedResponse[T]:
        total_pages = ceil(total / page_size) if page_size > 0 else 0
        has_prev = page_number > 1 and page_number <= total_pages + 1
        has_next = page_number < total_pages
        return cls(
            total=total,
            page_number=page_number,
            page_size=page_size,
            has_next=has_next,
            has_prev=has_prev,
            items=items,
        )
