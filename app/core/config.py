from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./fit_it.db"
    secret_key: str = "change_me"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
