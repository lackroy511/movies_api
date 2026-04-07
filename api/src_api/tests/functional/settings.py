import json
from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent.parent


class TestsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env",
        extra="ignore",
    )

    base_dir: Path = BASE_DIR

    movies_api_base_url: str = "http://movies_api:8010"
    
    elastic_base_url: str = "http://movies_elastic:9200"
    elastic_movies_index_name: str = "movies"
    elastic_genres_index_name: str = "genres"
    elastic_persons_index_name: str = "persons"
    
    redis_base_url: str = "redis://movies_redis:6379"
    
    @computed_field
    @property
    def elastic_movies_index_mapping(self) -> dict:
        with open(self.mapping_path / "es-movies-index.json", "r") as file:
            return json.load(file)

    @computed_field
    @property
    def elastic_genres_index_mapping(self) -> dict:
        with open(self.mapping_path / "es-genres-index.json", "r") as file:
            return json.load(file)
    
    @computed_field
    @property
    def elastic_persons_index_mapping(self) -> dict:
        with open(self.mapping_path / "es-persons-index.json", "r") as file:
            return json.load(file)
    
    @computed_field
    @property
    def mapping_path(self) -> Path:
        return self.base_dir.parent / ".docker"


test_settings = TestsSettings()
