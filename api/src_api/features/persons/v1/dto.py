from dataclasses import dataclass


@dataclass
class PersonDTO:
    id: str
    full_name: str


@dataclass
class PersonsListDTO:
    total: int
    items: list[PersonDTO]
