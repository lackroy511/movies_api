from pydantic import BaseModel, Field


class PersonResponse(BaseModel):
    id: str
    full_name: str = Field(description="Person full name")


class PersonDetailResponse(PersonResponse):
    pass


class PersonMovieResponse(BaseModel):
    id: str
    title: str = Field(description="Movie title")
    imdb_rating: float | None = Field(description="IMDB rating")
    roles: list[str] = Field(description="Person roles in movie")
