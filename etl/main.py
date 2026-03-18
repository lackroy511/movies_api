import logging

from src.config.settings import settings
from src.config.logger import configure_logging
from src.db.elastic_db import ElasticConnection
from src.db.psql_db import PSQLConnection, pool
from src.repositories.elastic_repo import ElasticRepository
from src.repositories.psql_repo import PSQLRepository
from src.services.etl import ETLService
from src.transform.psql_to_es import ToElasticDataTransformer
from src.utils.state import JsonFileStorage, State

configure_logging()
log = logging.getLogger(__name__)


def main() -> None:
    psql_conn = PSQLConnection()
    psql_repo = PSQLRepository(psql_conn)
    elastic_conn = ElasticConnection(settings.elastic_base_url)
    elastic_repo = ElasticRepository(elastic_conn)
    data_transformer = ToElasticDataTransformer(settings.elastic_index_name)
    storage = JsonFileStorage(settings.etl_state_file)
    state = State(storage)
    etl = ETLService(
        state,
        psql_repo,
        elastic_repo,
        data_transformer,
        batch_size=settings.batch_size,
    )
    
    try:
        log.info("Запуск ETL процесса...")
        etl.run()
    except Exception:
        log.exception("Ошибка ETL процесса, процесс завершен.")
    finally:
        pool.close()


if __name__ == "__main__":
    main()
