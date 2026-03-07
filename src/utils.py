import os
from typing import Any
from uuid import UUID

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

from src.dependencies import get_habit_service, get_task_service, get_theme_service
from src.schemas import Stats, ThemeResponse
from src.services import HabitService
from src.services.tasks import TaskService
from src.services.themes import ThemeService

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)


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


async def get_template_context(
    request: Request,
    theme_service: ThemeService = Depends(get_theme_service),
    statistics: Stats = Depends(get_stats),
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
    NoTheme = ThemeResponse(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        name="Все темы",
        color="#000000",
        is_active=selected_theme is None,
    )
    themes.insert(0, NoTheme)

    # Подсвечиваем выбранную тему
    if selected_theme is not None:
        for theme in themes:
            if theme.name == selected_theme:
                theme.is_active = True
                break

    return {"request": request, "themes": themes, "stats": statistics}


def error_context_updater(context: dict[Any, Any], e: str) -> dict[Any, Any]:
    context.update({"message_type": "error", "title": "Ошибка", "message": str(e)})
    return context
