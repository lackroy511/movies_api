from uuid import UUID
from pydantic import BaseModel


class GenreResponse(BaseModel):
    id: UUID
    name: str
    description: str | None