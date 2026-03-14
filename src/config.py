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

    CONTAINER_APP_PORT: int
    APP_PORT: int

    UI_SESSION_SECRET_KEY: str | None = None
    UI_SESSION_COOKIE_NAME: str = "habitflow_session"
    UI_SESSION_MAX_AGE: int = 60 * 60 * 24 * 14  # 14 days
    UI_SESSION_SAME_SITE: Literal["lax", "strict", "none"] = "lax"
    UI_SESSION_HTTPS_ONLY: bool = False

    AUTH_SESSION_COOKIE_NAME: str = "auth_session"
    AUTH_SESSION_MAX_AGE: int = 60 * 60 * 24 * 14  # 14 days
    AUTH_SESSION_SAME_SITE: Literal["lax", "strict", "none"] = "lax"
    AUTH_SESSION_HTTPS_ONLY: bool = False

    GOOGLE_OAUTH_CLIENT_ID: str | None = None
    GOOGLE_OAUTH_CLIENT_SECRET: str | None = None
    GOOGLE_OAUTH_REDIRECT_URI: str | None = None
    GOOGLE_OAUTH_STATE_TTL: int = 10 * 60  # 10 minutes

    ZENQUOTES_API_URL: str
    REFILL_INTERVAL_HOURS: int

    API_KEY: str
    DEBUG: bool

    @property
    def google_oauth_enabled(self) -> bool:
        return bool(
            self.GOOGLE_OAUTH_CLIENT_ID
            and self.GOOGLE_OAUTH_CLIENT_SECRET
            and self.GOOGLE_OAUTH_REDIRECT_URI
        )

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
        if self.UI_SESSION_SECRET_KEY:
            return self.UI_SESSION_SECRET_KEY
        if not self.DEBUG:
            raise ValueError("SECRET_KEY must be set when DEBUG=False")
        return secrets.token_urlsafe(32)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
