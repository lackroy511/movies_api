from src.db.elastic_db import ElasticConnection


class ElasticRepository:
    def __init__(self, connection: ElasticConnection) -> None:
        self.connection = connection

    def load_movies(self, data: str) -> None:
        self.connection.bulk(data)
