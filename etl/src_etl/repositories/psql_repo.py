from abc import ABC, abstractmethod

from src_etl.db.psql_db import PSQLConnection
from src_etl.dto.psql_dto import GenreDTO, MovieDTO, PersonDTO, PostgresDTO
from src_etl.repositories.queries import UPDATED_GENRES, UPDATED_MOVIES, UPDATED_PERSONS


class PSQLRepo(ABC):
    def __init__(self, connection: PSQLConnection) -> None:
        self.connection = connection
    
    @abstractmethod
    def get_updated_rows(
        self,
        last_updated: str,
        limit: int,
        offset: int,
    ) -> list[PostgresDTO]:
        ...


class MoviesPSQLRepo(PSQLRepo):
    def __init__(self, connection: PSQLConnection) -> None:
        super().__init__(connection)

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


class GenresPSQLRepo(PSQLRepo):
    def __init__(self, connection: PSQLConnection) -> None:
        super().__init__(connection)

    def get_updated_rows(
        self,
        last_updated: str,
        limit: int,
        offset: int,
    ) -> list[GenreDTO]:
        genres = self.connection.fetch(
            UPDATED_GENRES,
            last_updated,
            limit,
            offset,
        )
        return [GenreDTO(**genre) for genre in genres]


class PersonsPSQLRepo(PSQLRepo):
    def __init__(self, connection: PSQLConnection) -> None:
        super().__init__(connection)

    def get_updated_rows(
        self,
        last_updated: str,
        limit: int,
        offset: int,
    ) -> list[PersonDTO]:
        persons = self.connection.fetch(
            UPDATED_PERSONS,
            last_updated,
            limit,
            offset,
        )
        return [PersonDTO(**person) for person in persons]