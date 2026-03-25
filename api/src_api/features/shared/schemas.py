from pydantic import BaseModel, Field

from src_api.features.movies.v1.schemas import MovieResponse


class PaginatedResponse(BaseModel):
    total: int = Field(description="Total number of items")
    page_number: int = Field(description="Page number")
    page_size: int = Field(description="Page size")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")
    items: list[MovieResponse] = Field(description="List of items")