import secrets
from functools import cached_property
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DB: int

    APP_PORT: int

    SECRET_KEY: str | None = None
    SESSION_COOKIE_NAME: str = "habitflow_session"
    SESSION_MAX_AGE: int = 60 * 60 * 24 * 14  # 14 days
    SESSION_SAME_SITE: Literal["lax", "strict", "none"] = "lax"
    SESSION_HTTPS_ONLY: bool = False

    API_KEY: str
    DEBUG: bool

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_psycopg2(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def redis_dsn(self) -> str:
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @cached_property
    def session_secret_key(self) -> str:
        if self.SECRET_KEY:
            return self.SECRET_KEY
        if not self.DEBUG:
            raise ValueError("SECRET_KEY must be set when DEBUG=False")
        return secrets.token_urlsafe(32)

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
