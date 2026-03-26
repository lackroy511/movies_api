from src_etl.db.elastic_db import ElasticConnection


class ElasticRepo:
    def __init__(self, connection: ElasticConnection) -> None:
        self.connection = connection

    def load_movies(self, data: str) -> None:
        self.connection.bulk(data)


class MoviesElasticRepo(ElasticRepo):
    pass


class GenresElasticRepo(ElasticRepo):
    pass


class PersonsElasticRepo(ElasticRepo):
    pass