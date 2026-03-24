from uuid import UUID

from pydantic import BaseModel, Field


class MovieResponse(BaseModel):
    id: UUID
    title: str = Field(description="Movie title")
    description: str | None = Field(description="Movie description")
    imdb_rating: float | None = Field(description="IMDB rating")
    genres: list[str] = Field(description="Movie genres")
    directors_names: list[str] = Field(description="Directors names")
    actors_names: list[str] = Field(description="Actors names")
    writers_names: list[str] = Field(description="Writers names")
    directors: list[Person] = Field(description="Directors")
    actors: list[Person] = Field(description="Actors")
    writers: list[Person] = Field(description="Writers")


class Person(BaseModel):
    id: UUID
    name: str
