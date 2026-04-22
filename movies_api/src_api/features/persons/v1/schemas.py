from datetime import date
from pydantic import BaseModel, Field


class PersonResponse(BaseModel):
    id: str
    full_name: str = Field(description="Person full name")


class PersonDetailResponse(PersonResponse):
    pass


class PersonMovieResponse(BaseModel):
    id: str
    creation_date: date | None = Field(description="Creation date")
    file_path: str | None = Field(description="Path to movie file")
    title: str = Field(description="Movie title")
    imdb_rating: float | None = Field(description="IMDB rating")
    roles: list[str] = Field(description="Person roles in movie")
