
from pydantic import BaseModel, Field


class GenreResponse(BaseModel):
    id: str
    name: str = Field(description="Genre name")
    description: str | None = Field(description="Genre description")