from src.db.psql_db import PSQLConnection
from src.dto.psql_dto import MovieDTO
from src.repositories.queries import UPDATED_MOVIES


class PSQLRepository:
    def __init__(self, connection: PSQLConnection) -> None:
        self.connection = connection

    def get_updated_movies(
        self,
        last_updated: str,
        limit: int,
        offset: int,
    ) -> list[MovieDTO]:
        movies = self.connection.fetch(
            UPDATED_MOVIES,
            *[last_updated] * 3,
            limit,
            offset,
        )
        return [MovieDTO(**movie) for movie in movies]
