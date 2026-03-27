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