from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env",
        extra="ignore",
    )

    base_dir: Path = BASE_DIR
    log_level: str
    
    elastic_base_url: str
    elastic_movies_index_name: str
    elastic_genres_index_name: str
    elastic_persons_index_name: str
    
    redis_base_url: str
    redis_cache_ttl: int

    secret_key: str
    

settings = Settings()  # ty: ignore
