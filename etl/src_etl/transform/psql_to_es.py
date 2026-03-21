import json
from dataclasses import asdict

from src_etl.dto.elastic_dto import DocMetaDataDTO, MetaDataDTO, MovieDocDTO, PersonDTO
from src_etl.dto.psql_dto import MovieDTO, PersonRole


class ToElasticDataTransformer:
    def __init__(self, index_name: str) -> None:
        self.index_name = index_name

    def transform(self, movies: list[MovieDTO]) -> str:
        elastic_data = ""

        for movie in movies:
            doc_meta_data = DocMetaDataDTO(
                index=MetaDataDTO(
                    _index=self.index_name,
                    _id=str(movie.id),
                ),
            )
            movie_doc = MovieDocDTO(
                id=str(movie.id),
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
