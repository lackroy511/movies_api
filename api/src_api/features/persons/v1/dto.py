from uuid import UUID
from dataclasses import dataclass


@dataclass
class PersonsListDTO:
    total: int
    items: list[PersonDTO]


@dataclass(frozen=True)
class PersonDTO:
    id: str
    full_name: str


@dataclass
class PersonMoviesListDTO:
    total: int
    items: list[PersonMovieDTO]


@dataclass(frozen=True)
class PersonMovieDTO:
    id: UUID
    title: str
    description: str | None
    imdb_rating: float | None
    genres: list[str]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[MoviePerson]
    actors: list[MoviePerson]
    writers: list[MoviePerson]


@dataclass(frozen=True)
class MoviePerson:
    id: UUID
    name: str