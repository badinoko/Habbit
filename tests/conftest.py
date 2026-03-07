from collections.abc import Iterator
import os
import time
from uuid import uuid4

import docker
import httpx
import psycopg2
import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport
from psycopg2.extensions import connection as pg_connection
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


class DatabaseConfig(BaseSettings):
    user: str = Field(alias="DATABASE_USERNAME")
    name: str = Field(alias="DATABASE_NAME")
    password: str = Field(alias="DATABASE_PASSWORD")
    port: int = Field(alias="DATABASE_PORT")
    host: str = Field(alias="DATABASE_HOST")

    @property
    def dsn(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.user,
                host=self.host,
                port=self.port,
                path=self.name,
                password=self.password,
            )
        )

    @property
    def dsn_sync(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=self.user,
                host=self.host,
                port=self.port,
                path=self.name,
                password=self.password,
            )
        )


class TestConfig:
    database = DatabaseConfig(
        DATABASE_HOST="localhost",
        DATABASE_PORT=5433,
        DATABASE_USERNAME="postgres",
        DATABASE_PASSWORD="postgres",
        DATABASE_NAME="test_template",
    )


config = TestConfig.database


SAFE_TEST_ENV = {
    "DEBUG": "true",
    "TESTING": "true",
    "API_KEY": "test-api-key",
    "APP_PORT": "8000",
    "POSTGRES_HOST": config.host,
    "POSTGRES_PORT": str(config.port),
    "POSTGRES_USER": config.user,
    "POSTGRES_PASSWORD": config.password,
    "POSTGRES_DB": config.name,
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_PASSWORD": "redis",
    "REDIS_DB": "0",
    "DATABASE_HOST": config.host,
    "DATABASE_PORT": str(config.port),
    "DATABASE_USERNAME": config.user,
    "DATABASE_PASSWORD": config.password,
    "DATABASE_NAME": config.name,
}


def _set_safe_test_env() -> None:
    for key, value in SAFE_TEST_ENV.items():
        os.environ[key] = value


def _restore_env(snapshot: dict[str, str | None]) -> None:
    for key, value in snapshot.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


_ORIGINAL_TEST_ENV = {key: os.environ.get(key) for key in SAFE_TEST_ENV}
# Применяем env до импорта тестовых модулей: часть тестов импортирует app на этапе коллекции.
_set_safe_test_env()


@pytest.fixture(scope="session", autouse=True)
def safe_test_env() -> Iterator[None]:
    _set_safe_test_env()
    yield
    _restore_env(_ORIGINAL_TEST_ENV)


def get_db_connection(dbname=None) -> pg_connection:
    """Создает подключение к тестовой БД"""
    return psycopg2.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        dbname=dbname or config.name,  # Если dbname не указан, используем config.name
    )


@pytest.fixture(scope="session")
def postgres_container():
    container_name = f"test_postgres_{uuid4().hex[:8]}"
    try:
        client = docker.from_env()
        client.ping()
    except Exception as exc:
        pytest.skip(f"Docker is required for integration tests: {exc}")

    try:
        client.containers.run(
            image="postgres:15-alpine",
            name=container_name,
            environment={
                "POSTGRES_USER": config.user,
                "POSTGRES_PASSWORD": config.password,
                "POSTGRES_DB": config.name,
            },
            ports={"5432/tcp": config.port},
            detach=True,
            remove=True,
        )

        for _ in range(30):  # 30 попыток по 0.5 сек = 15 сек
            try:
                conn = get_db_connection()
                conn.close()
                break
            except psycopg2.OperationalError:
                time.sleep(0.5)
        else:
            raise Exception("PostgreSQL container failed to start")

        yield container_name

    finally:
        try:
            cont = client.containers.get(container_name)
            cont.stop(timeout=1)
        except docker.errors.NotFound:
            pass


@pytest.fixture(scope="session")
def template_db(postgres_container):
    """Создает шаблонную БД с примененными миграциями"""
    # Создаем шаблонную БД
    conn = get_db_connection(dbname="postgres")
    conn.autocommit = True
    cur = conn.cursor()

    # Удаляем шаблонную БД, если она уже существует (на случай перезапуска)
    cur.execute(f"DROP DATABASE IF EXISTS {config.name};")
    cur.execute(f"CREATE DATABASE {config.name};")
    cur.close()
    conn.close()

    # Применяем миграции к шаблонной БД
    run_alembic_migrations()
    conn = get_db_connection(dbname=config.name)
    cur = conn.cursor()
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
    cur.fetchall()
    conn.close()

    # Запрещаем подключения к шаблонной БД (требование для использования в качестве шаблона)
    conn = get_db_connection(dbname="postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"ALTER DATABASE {config.name} ALLOW_CONNECTIONS false;")
    cur.close()
    conn.close()


def run_alembic_migrations():
    """Применяет миграции Alembic синхронно к тестовой БД"""
    dsn = f"postgresql://{config.user}:{config.password}@{config.host}:{config.port}/{config.name}"
    os.environ["TESTING"] = "true"

    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.dirname(current_dir)
    migrations_path = os.path.join(base_path, "src", "database", "migrations")

    # Создаём конфиг без файла alembic.ini
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", migrations_path)
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)

    # Применяем миграции до головной версии
    command.upgrade(alembic_cfg, "head")


@pytest.fixture(scope="function")
def test_db(template_db):
    """Создает временную БД как клон шаблона и возвращает DSN"""
    tmp_name = f"test_{uuid4().hex}"

    # Подключаемся к системной БД для создания новой БД из шаблона
    conn = get_db_connection(dbname="postgres")
    conn.autocommit = True
    cur = conn.cursor()

    # Клонируем шаблон
    cur.execute(f"CREATE DATABASE {tmp_name} TEMPLATE {config.name};")
    cur.close()
    conn.close()

    # Возвращаем DSN для асинхронного подключения (используем asyncpg)
    dsn = f"postgresql+asyncpg://{config.user}:{config.password}@{config.host}:{config.port}/{tmp_name}"
    yield dsn

    # После теста удаляем временную БД
    conn = get_db_connection(dbname="postgres")
    conn.autocommit = True
    cur = conn.cursor()

    # Принудительно завершаем все соединения к временной БД
    cur.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{tmp_name}'
        AND pid <> pg_backend_pid();
    """)
    cur.execute(f"DROP DATABASE {tmp_name};")
    cur.close()
    conn.close()


@pytest.fixture
async def engine_async(test_db):
    """Создает async-движок для временной тестовой БД"""
    engine = create_async_engine(test_db)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> sessionmaker:
    """Фабрика для создания async-сессий"""
    return sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def session(session_factory_async):
    """Асинхронная сессия для работы с БД"""
    async with session_factory_async() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(session_factory_async):
    """
    Тестовый клиент FastAPI с переопределённой зависимостью БД.
    Использует временную тестовую БД через session_factory_async.
    """
    from src.database.connection import get_db
    from src.main import app

    async def override_get_db():
        async with session_factory_async() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # Подменяем зависимость
    app.dependency_overrides[get_db] = override_get_db

    # Создаём тестовый клиент
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()
