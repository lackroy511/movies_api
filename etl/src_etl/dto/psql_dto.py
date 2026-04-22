from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import TypedDict, TypeVar
from uuid import UUID

PostgresDTO = TypeVar("PostgresDTO", bound="BasePostgresDTO")


@dataclass(frozen=True)
class BasePostgresDTO:
    pass


@dataclass(frozen=True)
class MovieDTO(BasePostgresDTO):
    id: UUID
    creation_date: date | None
    file_path: str | None
    title: str
    description: str | None
    creation_date: date | None
    rating: float | None
    type: str
    created_at: datetime
    updated_at: datetime
    persons: list[Person]
    genres: list[str]


class Person(TypedDict):
    id: UUID
    role: PersonRole
    full_name: str


class PersonRole(str, Enum):
    ACTOR = "actor"
    WRITER = "writer"
    DIRECTOR = "director"


@dataclass(frozen=True)
class GenreDTO(BasePostgresDTO):
    id: UUID
    name: str
    description: str


@dataclass(frozen=True)
class PersonDTO(BasePostgresDTO):
    id: UUID
    full_name: str
