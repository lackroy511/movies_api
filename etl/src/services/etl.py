import logging
import time
from datetime import datetime, timezone

from src.dto.psql_dto import MovieDTO
from src.repositories.elastic_repo import ElasticRepository
from src.repositories.psql_repo import PSQLRepository
from src.transform.psql_to_es import ToElasticDataTransformer
from src.utils.state import State

log = logging.getLogger(__name__)


class ETLService:
    STATE_KEY = "last_updated"

    def __init__(
        self,
        state: State,
        psql_repo: PSQLRepository,
        elastic_repo: ElasticRepository,
        data_transformer: ToElasticDataTransformer,
        batch_size: int = 100,
    ) -> None:
        self.state = state
        self.psql_repo = psql_repo
        self.elastic_repo = elastic_repo
        self.data_transformer = data_transformer
        self.batch_size = batch_size

        self.psql_offset = 0
        self.is_first_iter = True

    def run(self) -> None:
        while True:
            if self.is_first_iter:
                last_updated = self.state.get_state(self.STATE_KEY)
                new_last_updated = (
                    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f") + "+00"
                )
                self.is_first_iter = False
                start = time.perf_counter()

            to_load = self._get_movies_to_load(last_updated)
            if not to_load:
                self.is_first_iter = True
                self.psql_offset = 0
                self.state.set_state(self.STATE_KEY, new_last_updated)
                duration = time.perf_counter() - start
                print(f"Процесс ETL завершен за {duration:.3f} сек")
                time.sleep(10)
                continue

            transformed_data = self.data_transformer.transform(to_load)
            self.elastic_repo.load_movies(transformed_data)
            self.psql_offset += self.batch_size
            log.info("Обновлено %r фильмов в Elasticsearch", len(to_load))
            
    def _get_movies_to_load(self, last_updated: str) -> list[MovieDTO]:
        query_params = (last_updated, self.batch_size, self.psql_offset)
        return self.psql_repo.get_updated_movies(*query_params)