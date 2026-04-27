from dataclasses import dataclass
from datetime import date


@dataclass
class PersonsListDTO:
    total: int
    items: list[PersonDTO]


@dataclass(frozen=True)
class PersonDTO:
    id: str
    full_name: str


@dataclass(frozen=True)
class PersonDetailDTO(PersonDTO):
    pass


@dataclass
class PersonMoviesListDTO:
    total: int
    items: list[PersonMovieDTO]


@dataclass(frozen=True)
class PersonMovieDTO:
    id: str
    creation_date: date | None
    file_path: str | None
    title: str
    imdb_rating: float | None
    roles: list[str]
    

@dataclass(frozen=True)
class MoviePerson:
    id: str
    name: str
