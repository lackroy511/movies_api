
from pydantic import BaseModel


class GenreResponse(BaseModel):
    id: str
    name: str
    description: str | None