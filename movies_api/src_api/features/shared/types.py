from typing import Literal, Protocol

SortMoviesType = Literal["imdb_rating", "-imdb_rating"]


class DataclassType(Protocol):
    __dataclass_fields__: dict
