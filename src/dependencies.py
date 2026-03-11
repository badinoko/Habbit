from functools import lru_cache
from typing import Annotated
from urllib.parse import quote

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.connection import get_db
from src.redis import RedisAdapter
from src.repositories import (
    AuthRepository,
    HabitRepository,
    RedisSessionStore,
    TaskRepository,
    ThemeRepository,
)
from src.schemas.auth import AuthUser
from src.services import HabitService, TaskService, ThemeService
from src.services.auth import AuthService

_AUTH_LOGIN_PATH = "/auth/login"


def _is_html_request(request: Request) -> bool:
    accept = request.headers.get("accept", "").lower()
    content_type = request.headers.get("content-type", "").lower()

    if "text/html" in accept:
        return True
    return any(
        expected_content_type in content_type
        for expected_content_type in (
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        )
    )


def _login_redirect_target(request: Request) -> str:
    original_target = request.url.path
    if request.url.query:
        original_target = f"{original_target}?{request.url.query}"
    return f"{_AUTH_LOGIN_PATH}?next={quote(original_target, safe='')}"


@lru_cache(maxsize=1)
def get_redis_adapter() -> RedisAdapter:
    return RedisAdapter()


async def get_auth_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthRepository:
    """Провайдер для auth-репозитория."""
    return AuthRepository(session=db)


async def get_session_store(
    redis_adapter: RedisAdapter = Depends(get_redis_adapter),
) -> RedisSessionStore:
    """Провайдер для session-store (Redis)."""
    return RedisSessionStore(redis_adapter=redis_adapter)


async def get_auth_service(
    auth_repo: AuthRepository = Depends(get_auth_repository),
    session_store: RedisSessionStore = Depends(get_session_store),
) -> AuthService:
    """Провайдер для auth-сервиса."""
    return AuthService(auth_repo=auth_repo, session_store=session_store)


async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthUser | None:
    """Достать пользователя по session-id из cookie через Redis и БД."""
    session_id = request.cookies.get(settings.AUTH_SESSION_COOKIE_NAME)
    if not session_id:
        return None

    normalized_session_id = session_id.strip()
    if not normalized_session_id:
        return None

    return await auth_service.resolve_user(session_id=normalized_session_id)


async def optional_user(
    current_user: AuthUser | None = Depends(get_current_user),
) -> AuthUser | None:
    """Опциональный пользователь: `None`, если не авторизован."""
    return current_user


async def require_auth(
    request: Request,
    current_user: AuthUser | None = Depends(get_current_user),
) -> AuthUser:
    """Требует авторизацию; для HTML делает redirect, иначе отдаёт 401 JSON."""
    if current_user is not None:
        return current_user

    if _is_html_request(request):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Authentication required",
            headers={"Location": _login_redirect_target(request)},
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )


async def get_theme_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AuthUser | None = Depends(get_current_user),
) -> ThemeRepository:
    """Провайдер для репозитория тем"""
    return ThemeRepository(
        session=db,
        owner_id=current_user.id if current_user is not None else None,
    )


async def get_user_theme_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AuthUser = Depends(require_auth),
) -> ThemeRepository:
    """Провайдер для репозитория тем с обязательной авторизацией."""
    return ThemeRepository(session=db, owner_id=current_user.id)


async def get_theme_service(
    theme_repo: ThemeRepository = Depends(get_theme_repository),
) -> ThemeService:
    """Провайдер для сервиса тем"""
    return ThemeService(theme_repo=theme_repo)


async def get_user_theme_service(
    theme_repo: ThemeRepository = Depends(get_user_theme_repository),
) -> ThemeService:
    """Провайдер для сервиса тем с обязательной авторизацией."""
    return ThemeService(theme_repo=theme_repo)


async def get_task_repository(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser | None = Depends(get_current_user),
) -> TaskRepository:
    return TaskRepository(
        session=db,
        owner_id=current_user.id if current_user is not None else None,
    )


async def get_user_task_repository(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Depends(require_auth),
) -> TaskRepository:
    """Провайдер для репозитория задач с обязательной авторизацией."""
    return TaskRepository(session=db, owner_id=current_user.id)


async def get_task_service(
    task_repo: TaskRepository = Depends(get_task_repository),
    theme_repo: ThemeRepository = Depends(get_theme_repository),
) -> TaskService:
    """Провайдер для сервиса задач"""
    return TaskService(task_repo=task_repo, theme_repo=theme_repo)


async def get_user_task_service(
    task_repo: TaskRepository = Depends(get_user_task_repository),
    theme_repo: ThemeRepository = Depends(get_user_theme_repository),
) -> TaskService:
    """Провайдер для сервиса задач с обязательной авторизацией."""
    return TaskService(task_repo=task_repo, theme_repo=theme_repo)


async def get_habit_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AuthUser | None = Depends(get_current_user),
) -> HabitRepository:
    """Провайдер для репозитория привычек"""
    return HabitRepository(
        session=db,
        owner_id=current_user.id if current_user is not None else None,
    )


async def get_user_habit_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AuthUser = Depends(require_auth),
) -> HabitRepository:
    """Провайдер для репозитория привычек с обязательной авторизацией."""
    return HabitRepository(session=db, owner_id=current_user.id)


async def get_habit_service(
    habit_repo: HabitRepository = Depends(get_habit_repository),
    theme_repo: ThemeRepository = Depends(get_theme_repository),
) -> HabitService:
    """Провайдер для сервиса привычек"""
    return HabitService(habit_repo=habit_repo, theme_repo=theme_repo)


async def get_user_habit_service(
    habit_repo: HabitRepository = Depends(get_user_habit_repository),
    theme_repo: ThemeRepository = Depends(get_user_theme_repository),
) -> HabitService:
    """Провайдер для сервиса привычек с обязательной авторизацией."""
    return HabitService(habit_repo=habit_repo, theme_repo=theme_repo)
