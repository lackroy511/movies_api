from pydantic import BaseModel


class PersonResponse(BaseModel):
    id: str
    full_name: str


class PersonMovieResponse(BaseModel):
    id: str
    title: str
    imdb_rating: float | None
    roles: list[str]
