from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env",
        extra="ignore",
    )

    base_dir: Path = BASE_DIR
    
    batch_size: int = 100

    postgres_db: str
    postgres_user: str
    postgres_password: str
    db_host: str
    db_port: int

    elastic_base_url: str = "http://localhost:9200"
    elastic_movies_index_name: str = "movies"
    elastic_genres_index_name: str = "genres"
    elastic_persons_index_name: str = "persons"

    log_level: str = "INFO"
    
    @computed_field
    @property
    def psql_dsn(self) -> str:
        return (
            f"dbname={self.postgres_db} "
            f"user={self.postgres_user} "
            f"password={self.postgres_password} "
            f"host={self.db_host} "
            f"port={self.db_port}"
        )


settings = Settings()  # ty: ignore
