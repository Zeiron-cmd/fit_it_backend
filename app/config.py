from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BACKEND_PUBLIC_URL: str = "http://localhost:8000"
    PROJECT_NAME: str = "Fit it Backend"

    DATABASE_URL: str = (
        "postgresql+psycopg2://fit_it:fit_it_password@db:5432/fit_it"
    )

    JWT_SECRET_KEY: str = "change_this_secret_key_in_env"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SESSION_SECRET_KEY: str = "change_this_session_secret_in_env"

    FRONTEND_URL: str = "http://localhost:5173"
    FRONTEND_OAUTH_REDIRECT_URL: Optional[str] = None

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    YANDEX_CLIENT_ID: Optional[str] = None
    YANDEX_CLIENT_SECRET: Optional[str] = None

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()