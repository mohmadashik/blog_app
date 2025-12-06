from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Blob App"
    API_PREFIX: str = "/api"

    DATABASE_URL: str = "sqlite:///./dev.db"

    SECRET_KEY: str = "change-me-in-env"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    CORS_ORIGINS: List[AnyHttpUrl] = []

    class Config:
        env_file = ".env"


settings = Settings()
