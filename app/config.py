import os


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "crm-secret-key-change-in-production-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./crm.db")


settings = Settings()
