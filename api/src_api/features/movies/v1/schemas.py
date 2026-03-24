from uuid import UUID

from pydantic import BaseModel


class MovieResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    imdb_rating: float | None
    genres: list[str]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[Person]
    actors: list[Person]
    writers: list[Person]


class Person(BaseModel):
    id: UUID
    name: str
