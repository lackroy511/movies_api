from typing import Literal, Protocol

SortMoviesType = Literal[
    "imdb_rating",
    "-imdb_rating",
    "creation_date",
    "-creation_date",
]


class DataclassType(Protocol):
    __dataclass_fields__: dict


RolesType = Literal["admin", "subscriber"]