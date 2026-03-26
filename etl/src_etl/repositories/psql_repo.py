from abc import abstractmethod, ABC

from src_etl.db.psql_db import PSQLConnection
from src_etl.dto.psql_dto import MovieDTO, PostgresDTO
from src_etl.repositories.queries import UPDATED_MOVIES


class PSQLRepository(ABC):
    @abstractmethod
    def get_updated_rows(
        self,
        last_updated: str,
        limit: int,
        offset: int,
    ) -> list[PostgresDTO]:
        ...


class MoviesPSQLRepository(PSQLRepository):
    def __init__(self, connection: PSQLConnection) -> None:
        self.connection = connection

    def get_updated_rows(
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
