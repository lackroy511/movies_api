from dataclasses import dataclass
from uuid import UUID


@dataclass
class MoviesListDTO:
    total: int
    items: list[MovieDTO]


@dataclass
class MovieDTO:
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


@dataclass
class Person:
    id: UUID
    name: str
