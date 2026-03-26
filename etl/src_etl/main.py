import logging

from src_etl.config.settings import settings
from src_etl.config.logger import configure_logging
from src_etl.db.elastic_db import ElasticConnection
from src_etl.db.psql_db import PSQLConnection, pool
from src_etl.repositories.elastic_repo import ElasticRepository
from src_etl.repositories.psql_repo import MoviesPSQLRepository
from src_etl.services.etl import ETLService
from src_etl.transform.psql_to_es import MoviesToElasticDataTransformer
from src_etl.utils.state import JsonFileStorage, State

configure_logging()
log = logging.getLogger(__name__)


def main() -> None:
    psql_conn = PSQLConnection()
    elastic_conn = ElasticConnection(settings.elastic_base_url)
    storage = JsonFileStorage(settings.etl_state_file)
    
    movies_etl = get_movies_etl_service(psql_conn, elastic_conn, storage)
    try:
        log.info("Запуск ETL процесса...")
        movies_etl.run()
    except Exception:
        log.exception("Ошибка ETL процесса, процесс завершен.")
    finally:
        pool.close()


def get_movies_etl_service(
    psql_conn: PSQLConnection,
    elastic_conn: ElasticConnection,
    storage: JsonFileStorage,
) -> ETLService:
    psql_repo = MoviesPSQLRepository(psql_conn)
    elastic_repo = ElasticRepository(elastic_conn)
    transformer = MoviesToElasticDataTransformer(settings.elastic_movies_index_name) 
    state = State(storage, state_key="movies_last_updated")
    return ETLService(
        state,
        psql_repo,
        elastic_repo,
        transformer,
        settings.batch_size,
    )


if __name__ == "__main__":
    main()
