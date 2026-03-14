import os
import re
import secrets
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

from src.dependencies import (
    get_current_user,
    get_habit_service,
    get_task_service,
    get_theme_service,
)
from src.schemas import Stats, ThemeResponse
from src.schemas.auth import AuthUser
from src.schemas.statistics import StatisticsPageData
from src.services import HabitService
from src.services.tasks import TaskService
from src.services.themes import ThemeService

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)


def get_user_display_name(user: AuthUser | None) -> str | None:
    if user is None:
        return None

    local_part = user.email.split("@", 1)[0].strip()
    if not local_part:
        return user.email

    chunks = [chunk for chunk in re.split(r"[._-]+", local_part) if chunk]
    if not chunks:
        return local_part
    return " ".join(chunk.capitalize() for chunk in chunks[:2])


def ensure_csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if isinstance(token, str) and token:
        return token

    token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = token
    return token


async def get_stats(
    task_service: TaskService = Depends(get_task_service),
    habits_service: HabitService = Depends(get_habit_service),
) -> Stats:
    task_statistics = await task_service.get_task_statistics()
    habit_statistics = await habits_service.get_habit_statistics()
    return Stats(
        total_tasks=task_statistics.total,
        active_tasks=task_statistics.pending,
        total_habits=habit_statistics.total,
        success_rate=habit_statistics.success_rate,
        active_habits=habit_statistics.active,
        due_habits_today=habit_statistics.due_today,
        completed_habits_today=habit_statistics.completed_today,
    )


def get_stats_from_page_data(page_data: StatisticsPageData) -> Stats:
    return Stats(
        total_tasks=page_data.tasks.total,
        active_tasks=page_data.tasks.active,
        total_habits=page_data.habits.total,
        success_rate=page_data.habits.success_rate_today,
        active_habits=page_data.habits.active,
        due_habits_today=page_data.habits.due_today,
        completed_habits_today=page_data.habits.completed_today,
    )


async def build_template_context(
    request: Request,
    *,
    theme_service: ThemeService,
    statistics: Stats,
    current_user: AuthUser | None = None,
) -> dict[str, Any]:
    themes = await theme_service.list_themes(limit=None)

    params = request.query_params
    if params.get("theme"):
        if params["theme"] == "Все темы":
            request.session["selected_theme"] = None
            selected_theme = None
        else:
            request.session["selected_theme"] = params["theme"]
            selected_theme = params["theme"]
    else:
        selected_theme = request.session.get("selected_theme")

    # Темы заданной в сессии не существует
    if selected_theme is not None and not any(
        theme.name == selected_theme for theme in themes
    ):
        request.session["selected_theme"] = None
        selected_theme = None

    # Добавляем опцию "Все темы"
    no_theme = ThemeResponse(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        name="Все темы",
        color="#000000",
        is_active=selected_theme is None,
    )
    themes.insert(0, no_theme)

    # Подсвечиваем выбранную тему
    if selected_theme is not None:
        for theme in themes:
            if theme.name == selected_theme:
                theme.is_active = True
                break

    return {
        "request": request,
        "themes": themes,
        "stats": statistics,
        "current_user": current_user,
        "current_user_display_name": get_user_display_name(current_user),
        "csrf_token": ensure_csrf_token(request),
    }


async def get_template_context(
    request: Request,
    theme_service: ThemeService = Depends(get_theme_service),
    statistics: Stats = Depends(get_stats),
    current_user: Annotated[AuthUser | None, Depends(get_current_user)] = None,
) -> dict[str, Any]:
    return await build_template_context(
        request,
        theme_service=theme_service,
        statistics=statistics,
        current_user=current_user,
    )


def error_context_updater(context: dict[Any, Any], e: str) -> dict[Any, Any]:
    context.update({"message_type": "error", "title": "Ошибка", "message": str(e)})
    return context
