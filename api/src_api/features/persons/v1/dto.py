from dataclasses import dataclass


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
    movies: list[PersonMovieDTO]


@dataclass
class PersonMoviesListDTO:
    total: int
    items: list[PersonMovieDTO]


@dataclass(frozen=True)
class PersonMovieDTO:
    id: str
    title: str
    imdb_rating: float | None
    roles: list[str]
    

@dataclass(frozen=True)
class MoviePerson:
    id: str
    name: str
