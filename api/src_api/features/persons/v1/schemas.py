from pydantic import BaseModel


class PersonResponse(BaseModel):
    id: str
    full_name: str


class PersonDetailResponse(PersonResponse):
    movies: list[PersonMovieResponse]


class PersonMovieResponse(BaseModel):
    id: str
    title: str
    imdb_rating: float | None
    roles: list[str]
