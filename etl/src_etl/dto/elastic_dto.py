from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class DocMetaDataDTO:
    index: MetaDataDTO


@dataclass(frozen=True)
class MetaDataDTO:
    _index: str
    _id: str


@dataclass(frozen=True)
class MovieDocDTO:
    id: str
    title: str
    description: str | None
    imdb_rating: float | None
    genres: List[str]
    directors_names: List[str]
    actors_names: List[str]
    writers_names: List[str]
    directors: List[PersonDTO]
    actors: List[PersonDTO]
    writers: List[PersonDTO]


@dataclass(frozen=True)
class PersonDTO:
    id: str
    name: str


@dataclass(frozen=True)
class GenreDocDTO:
    id: str
    name: str
    description: str
    

@dataclass(frozen=True)
class PersonDocDTO:
    id: str
    full_name: str