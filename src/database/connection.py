import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings

logger = logging.getLogger("sqlalchemy.engine")


engine = create_async_engine(
    settings.DATABASE_URL_asyncpg,
    echo=settings.DEBUG,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


def get_engine() -> AsyncEngine:
    return engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection для FastAPI
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
