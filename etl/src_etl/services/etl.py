import logging
import time
from datetime import datetime, timezone

from src_etl.dto.psql_dto import PostgresDTO
from src_etl.repositories.elastic_repo import ElasticRepo
from src_etl.repositories.psql_repo import PSQLRepo
from src_etl.transform.psql_to_es import ToElasticDataTransformer
from src_etl.utils.state import State

log = logging.getLogger(__name__)


class ETLService:
    def __init__(
        self,
        state: State,
        psql_repo: PSQLRepo,
        elastic_repo: ElasticRepo,
        data_transformer: ToElasticDataTransformer,
        batch_size: int,
    ) -> None:
        self.state = state
        self.psql_repo = psql_repo
        self.elastic_repo = elastic_repo
        self.data_transformer = data_transformer
        self.batch_size = batch_size

        self.psql_offset = 0
        self.is_first_iter = True

    def run(self) -> None:
        log.info(
            "Запуск ETL процесса для индекса %r",
            self.data_transformer.index_name,
        )
        while True:
            if self.is_first_iter:
                last_updated = self.state.get_state(self.state.state_key)
                new_last_updated = (
                    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f") + "+00"
                )
                self.is_first_iter = False

            to_load = self._get_data_to_load(last_updated)
            if not to_load:
                self.is_first_iter = True
                self.psql_offset = 0
                self.state.set_state(self.state.state_key, new_last_updated)
                time.sleep(10)
                continue

            transformed_data = self.data_transformer.transform(to_load)
            self.elastic_repo.load_movies(transformed_data)
            self.psql_offset += self.batch_size
            log.info(
                "Обновлено %r записей в индексе %r",
                len(to_load),
                self.data_transformer.index_name,
            )

    def _get_data_to_load(self, last_updated: str) -> list[PostgresDTO]:
        return self.psql_repo.get_updated_rows(
            last_updated,
            self.batch_size,
            self.psql_offset,
        )
