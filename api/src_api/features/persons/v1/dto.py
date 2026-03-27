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
    person_id: str
    person_full_name: str
    movie_id: str
    movie_title: str
    description: str | None
    imdb_rating: float | None
    roles: list[str]
    

@dataclass(frozen=True)
class MoviePerson:
    id: str
    name: str