from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/educrm_db"
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    SECRET_KEY: str = "super-secret-key-minimum-32-characters-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_ENV: str = "development"
    DEBUG: bool = True
    WORKERS: int = 2
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # File Storage
    MEDIA_ROOT: str = "./media"
    MAX_UPLOAD_SIZE_MB: int = 5

    # DigitalOcean Spaces (prod da faollashtirish)
    USE_SPACES: bool = False
    DO_SPACES_KEY: str = ""
    DO_SPACES_SECRET: str = ""
    DO_SPACES_REGION: str = "fra1"
    DO_SPACES_BUCKET: str = "educrm-media"
    DO_SPACES_ENDPOINT: str = "https://fra1.digitaloceanspaces.com"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
