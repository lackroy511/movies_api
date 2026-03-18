from typing import LiteralString

from src.db.psql_db import PSQLConnection
from src.dto.psql_dto import MovieDTO, MovieIdDTO
from src.repositories.queries import (
    MOVIE_IDS_FOR_UPDATED_GENRES,
    MOVIE_IDS_FOR_UPDATED_PERSON_ROLES,
    MOVIE_IDS_FOR_UPDATED_PERSONS,
    MOVIES_BY_IDS,
    UPDATED_MOVIE_IDS,
)


class PSQLRepository:
    def __init__(self, connection: PSQLConnection) -> None:
        self.connection = connection

    def get_movies_by_ids(self, ids: list) -> list[MovieDTO]:
        movies = self.connection.fetch(MOVIES_BY_IDS, ids)
        return [MovieDTO(**movie) for movie in movies]

    def get_upd_movie_ids(
        self,
        last_updated: str,
        limit: int,
        offset: int,
    ) -> list[MovieIdDTO]:
        return self._get_movie_ids(
            UPDATED_MOVIE_IDS,
            last_updated,
            limit,
            offset,
        )

    def get_movie_ids_for_upd_persons(
        self,
        last_updated: str,
        limit: int,
        offset: int,
    ) -> list[MovieIdDTO]:
        return self._get_movie_ids(
            MOVIE_IDS_FOR_UPDATED_PERSONS,
            last_updated,
            limit,
            offset,
        )

    def get_movie_ids_for_upd_person_roles(
        self,
        last_updated: str,
        limit: int,
        offset: int,
    ) -> list[MovieIdDTO]:
        return self._get_movie_ids(
            MOVIE_IDS_FOR_UPDATED_PERSON_ROLES,
            last_updated,
            limit,
            offset,
        )

    def get_movie_ids_for_upd_genres(
        self,
        last_updated: str,
        limit: int,
        offset: int,
    ) -> list[MovieIdDTO]:
        return self._get_movie_ids(
            MOVIE_IDS_FOR_UPDATED_GENRES,
            last_updated,
            limit,
            offset,
        )

    def _get_movie_ids(
        self,
        query: LiteralString,
        *params: str | int | float | list,
    ) -> list[MovieIdDTO]:
        ids = self.connection.fetch(query, *params)
        return [MovieIdDTO(**item) for item in ids]
