from dataclasses import dataclass
from typing import List
from uuid import UUID


@dataclass
class Genre:
    id: str
    name: str
    description: str | None


@dataclass
class GenresListDTO:
    total: int
    items: List[Genre]