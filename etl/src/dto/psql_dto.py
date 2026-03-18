from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import TypedDict
from uuid import UUID


class PersonRole(str, Enum):
    ACTOR = "actor"
    WRITER = "writer"
    DIRECTOR = "director"


@dataclass(frozen=True)
class MovieIdDTO:
    id: UUID


@dataclass(frozen=True)
class MovieDTO:
    id: UUID
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
