from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env",
        extra="ignore",
    )

    base_dir: Path = BASE_DIR

    elastic_base_url: str = "http://localhost:9200"
    elastic_movies_index_name: str = "movies"
    elastic_genres_index_name: str = "genres"
    elastic_persons_index_name: str = "persons"
    
    redis_base_url: str = "redis://movies_redis:6379"
    redis_cache_ttl: int = 60 * 5
    
    log_level: str = "INFO"


settings = Settings()
