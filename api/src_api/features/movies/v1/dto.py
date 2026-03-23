from dataclasses import dataclass


@dataclass
class Movie:
    id: int
    title: str
    description: str
    imdb_rating: float
    genres: list[str]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[Person]
    actors: list[Person]
    writers: list[Person]


@dataclass
class Person:
    id: int
    name: str
