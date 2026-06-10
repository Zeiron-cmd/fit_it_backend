import os
from functools import lru_cache
from typing import Optional



from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./fit_it.db"
    secret_key: str = "change_me"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"


settings = Settings()

class Settings:
    """Application settings loaded from environment variables."""
    BACKEND_PUBLIC_URL: str = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Fit it Backend")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://fit_it:fit_it_password@db:5432/fit_it",
    )

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change_this_secret_key_in_env")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "change_this_session_secret_in_env")

    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    FRONTEND_OAUTH_REDIRECT_URL: Optional[str] = os.getenv("FRONTEND_OAUTH_REDIRECT_URL")

    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")

    GITHUB_CLIENT_ID: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")

    YANDEX_CLIENT_ID: Optional[str] = os.getenv("YANDEX_CLIENT_ID")
    YANDEX_CLIENT_SECRET: Optional[str] = os.getenv("YANDEX_CLIENT_SECRET")

    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


@lru_cache
def get_settings() -> Settings:
    return Settings()


