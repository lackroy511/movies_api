import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event

from src_etl.config.logger import configure_logging
from src_etl.config.settings import settings
from src_etl.db.elastic_db import ElasticConnection
from src_etl.db.psql_db import PSQLConnection
from src_etl.db.psql_db import pool as psql_pool
from src_etl.services.fabric import ETLServiceFabric

thread_pool = ThreadPoolExecutor(max_workers=3)
stop_event = Event()

configure_logging()
log = logging.getLogger(__name__)


def main() -> None:
    fabric = ETLServiceFabric()

    psql_conn = PSQLConnection()
    elastic_conn = ElasticConnection(settings.elastic_base_url)

    movies_etl = fabric.get_movies_etl_service(psql_conn, elastic_conn)
    genres_etl = fabric.get_genres_etl_service(psql_conn, elastic_conn)
    persons_etl = fabric.get_persons_etl_service(psql_conn, elastic_conn)
    try:
        with thread_pool as executor:
            threads = [
                executor.submit(etl.run, stop_event)
                for etl in [movies_etl, genres_etl, persons_etl]
            ]
            for thread in as_completed(threads):
                try:
                    thread.result()
                except Exception:
                    stop_event.set()
                    log.info("Закрываю потоки")
                    executor.shutdown(wait=True)
                    raise

    except Exception:
        log.exception("Ошибка ETL процесса, процесс завершен.")
    finally:
        psql_pool.close()


if __name__ == "__main__":
    main()
