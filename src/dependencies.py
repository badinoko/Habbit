from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db
from src.repositories import TaskRepository, ThemeRepository
from src.services import TaskService, ThemeService


async def get_theme_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ThemeRepository:
    """Провайдер для репозитория тем"""
    return ThemeRepository(session=db)


async def get_theme_service(
    theme_repo: ThemeRepository = Depends(get_theme_repository),
) -> ThemeService:
    """Провайдер для сервиса тем"""
    return ThemeService(theme_repo=theme_repo)


async def get_task_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskRepository:
    """Провайдер для репозитория задач"""
    return TaskRepository(session=db)


async def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    theme_repo: ThemeRepository = Depends(get_theme_repository),
) -> TaskService:
    """Провайдер для сервиса задач"""
    return TaskService(task_repo=task_repo, theme_repo=theme_repo)
