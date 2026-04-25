import json
from abc import ABC, abstractmethod
from dataclasses import asdict

from src_etl.dto.elastic_dto import (
    DocMetaDataDTO,
    GenreDocDTO,
    MetaDataDTO,
    MovieDocDTO,
    PersonDocDTO,
    PersonDTO,
)
from src_etl.dto.psql_dto import GenreDTO, MovieDTO
from src_etl.dto.psql_dto import PersonDTO as PostgresPersonDTO
from src_etl.dto.psql_dto import PersonRole, PostgresDTO


class ToElasticDataTransformer(ABC):
    def __init__(self, index_name: str) -> None:
        self.index_name = index_name

    @abstractmethod
    def transform(self, items: list[PostgresDTO]) -> str: ...


class MoviesToElasticDataTransformer(ToElasticDataTransformer):
    def __init__(self, index_name: str) -> None:
        super().__init__(index_name)

    def transform(self, items: list[MovieDTO]) -> str:
        elastic_data = ""
        for movie in items:
            doc_meta_data = DocMetaDataDTO(
                index=MetaDataDTO(
                    _index=self.index_name,
                    _id=str(movie.id),
                ),
            )
            movie_doc = MovieDocDTO(
                id=str(movie.id),
                creation_date=str(movie.creation_date) if movie.creation_date else None,
                file_path=movie.file_path,
                title=movie.title,
                description=movie.description,
                imdb_rating=movie.rating,
                genres=movie.genres,
                directors_names=[
                    person["full_name"]
                    for person in movie.persons
                    if person["role"] == PersonRole.DIRECTOR
                ],
                actors_names=[
                    person["full_name"]
                    for person in movie.persons
                    if person["role"] == PersonRole.ACTOR
                ],
                writers_names=[
                    person["full_name"]
                    for person in movie.persons
                    if person["role"] == PersonRole.WRITER
                ],
                directors=[
                    PersonDTO(id=str(person["id"]), name=person["full_name"])
                    for person in movie.persons
                    if person["role"] == PersonRole.DIRECTOR
                ],
                actors=[
                    PersonDTO(id=str(person["id"]), name=person["full_name"])
                    for person in movie.persons
                    if person["role"] == PersonRole.ACTOR
                ],
                writers=[
                    PersonDTO(id=str(person["id"]), name=person["full_name"])
                    for person in movie.persons
                    if person["role"] == PersonRole.WRITER
                ],
            )
            elastic_data += json.dumps(asdict(doc_meta_data)) + "\n"
            elastic_data += json.dumps(asdict(movie_doc)) + "\n"

        return elastic_data


class GenresToElasticDataTransformer(ToElasticDataTransformer):
    def __init__(self, index_name: str) -> None:
        super().__init__(index_name)

    def transform(self, items: list[GenreDTO]) -> str:
        elastic_data = ""
        for genre in items:
            doc_meta_data = DocMetaDataDTO(
                index=MetaDataDTO(
                    _index=self.index_name,
                    _id=str(genre.id),
                ),
            )
            movie_doc = GenreDocDTO(
                id=str(genre.id),
                name=genre.name,
                description=genre.description,
            )
            elastic_data += json.dumps(asdict(doc_meta_data)) + "\n"
            elastic_data += json.dumps(asdict(movie_doc)) + "\n"

        return elastic_data


class PersonsToElasticDataTransformer(ToElasticDataTransformer):
    def __init__(self, index_name: str) -> None:
        super().__init__(index_name)

    def transform(self, items: list[PostgresPersonDTO]) -> str:
        elastic_data = ""
        for person in items:
            doc_meta_data = DocMetaDataDTO(
                index=MetaDataDTO(
                    _index=self.index_name,
                    _id=str(person.id),
                ),
            )
            movie_doc = PersonDocDTO(
                id=str(person.id),
                full_name=person.full_name,
            )
            elastic_data += json.dumps(asdict(doc_meta_data)) + "\n"
            elastic_data += json.dumps(asdict(movie_doc)) + "\n"

        return elastic_data
