from uuid import UUID

from pydantic import BaseModel


class PersonResponse(BaseModel):
    id: UUID
    full_name: str


class PersonMovieResponse(BaseModel):
    id: UUID
    title: str
    imdb_rating: float | None
