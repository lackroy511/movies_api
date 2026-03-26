from src_etl.config.settings import settings
from src_etl.db.elastic_db import ElasticConnection
from src_etl.db.psql_db import PSQLConnection
from src_etl.repositories.elastic_repo import (
    GenresElasticRepo,
    MoviesElasticRepo,
    PersonsElasticRepo,
)
from src_etl.repositories.psql_repo import (
    GenresPSQLRepo,
    MoviesPSQLRepo,
    PersonsPSQLRepo,
)
from src_etl.services.etl import ETLService
from src_etl.transform.psql_to_es import (
    GenresToElasticDataTransformer,
    MoviesToElasticDataTransformer,
    PersonsToElasticDataTransformer,
)
from src_etl.utils.state import JsonFileStorage, State


class ETLServiceFabric:
    def get_movies_etl_service(
        self,
        psql_conn: PSQLConnection,
        elastic_conn: ElasticConnection,
        storage: JsonFileStorage,
    ) -> ETLService:
        psql_repo = MoviesPSQLRepo(psql_conn)
        elastic_repo = MoviesElasticRepo(elastic_conn)
        data_tr = MoviesToElasticDataTransformer(settings.elastic_movies_index_name)
        state = State(storage, state_key="movies_last_updated")
        return ETLService(
            state,
            psql_repo,
            elastic_repo,
            data_tr,
            settings.batch_size,
        )

    def get_genres_etl_service(
        self,
        psql_conn: PSQLConnection,
        elastic_conn: ElasticConnection,
        storage: JsonFileStorage,
    ) -> ETLService:
        psql_repo = GenresPSQLRepo(psql_conn)
        elastic_repo = GenresElasticRepo(elastic_conn)
        data_tr = GenresToElasticDataTransformer(settings.elastic_genres_index_name)
        state = State(storage, state_key="genres_last_updated")
        return ETLService(
            state,
            psql_repo,
            elastic_repo,
            data_tr,
            settings.batch_size,
        )

    def get_persons_etl_service(
        self,
        psql_conn: PSQLConnection,
        elastic_conn: ElasticConnection,
        storage: JsonFileStorage,
    ) -> ETLService:
        psql_repo = PersonsPSQLRepo(psql_conn)
        elastic_repo = PersonsElasticRepo(elastic_conn)
        data_tr = PersonsToElasticDataTransformer(settings.elastic_persons_index_name)
        state = State(storage, state_key="persons_last_updated")
        return ETLService(
            state,
            psql_repo,
            elastic_repo,
            data_tr,
            settings.batch_size,
        )
