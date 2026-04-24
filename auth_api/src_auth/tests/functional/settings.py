from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent.parent


class TestsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    base_dir: Path = BASE_DIR

    auth_api_base_url: str = "http://movies_api:8020/api/auth"
    redis_base_url: str = "redis://auth_redis:6379"
    
    postgres_db: str
    postgres_user: str
    postgres_password: str
    db_host: str
    db_port: int
    
    admin_email: str
    
    @computed_field
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.db_port}/{self.postgres_db}"  # noqa: E501


test_settings = TestsSettings()  # ty: ignore


print(test_settings.base_dir)