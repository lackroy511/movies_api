from dataclasses import dataclass


@dataclass
class MoviesListDTO:
    total: int
    items: list[MovieDTO]


@dataclass(frozen=False)
class MovieDTO:
    id: str
    creation_date: str | None
    file_path: str | None
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
    id: str
    name: str
