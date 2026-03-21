from contextlib import contextmanager
from typing import Any, Generator, LiteralString, cast

import psycopg
import psycopg_pool
from psycopg.cursor import Cursor
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from src_etl.config.settings import settings
from src_etl.utils.backoff import Backoff

pool = ConnectionPool(
    settings.psql_dsn,
    min_size=1,
    max_size=2,
    kwargs={"options": "-c statement_timeout=5000"},
)


RETRY_EXCEPTIONS = (
    psycopg.OperationalError,
    psycopg.InterfaceError,
    psycopg_pool.PoolTimeout,
)


class PSQLConnection:
    @Backoff(RETRY_EXCEPTIONS)
    def fetch(
        self,
        query: LiteralString,
        *params: str | int | float | list,
    ) -> list[dict[str, Any]]:
        with self._get_cursor() as cur:
            result = cur.execute(query, params)
            return cast(list[dict[str, Any]], result.fetchall())

    @contextmanager
    def _get_cursor(self) -> Generator[Cursor, None, None]:
        global pool
        with (
            pool.connection() as conn,
            conn.cursor(row_factory=dict_row) as cur,
        ):
            yield cur
