from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.config import settings
from src.dependencies import get_habit_service, get_task_service
from src.routers.habits import router as habits_router
from src.routers.tasks import router as tasks_router
from src.routers.themes import router as themes_router
from src.services.habits import HabitService
from src.services.tasks import TaskService
from src.utils import get_template_context, templates

app = FastAPI(title="HabitFlow", description="Трекер привычек и задач", version="1.0.0")

app.mount("/static", StaticFiles(directory="src/static"), name="static")


app.include_router(themes_router)
app.include_router(tasks_router)
app.include_router(habits_router)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    session_cookie=settings.SESSION_COOKIE_NAME,
    max_age=settings.SESSION_MAX_AGE,
    same_site=settings.SESSION_SAME_SITE,
    https_only=settings.SESSION_HTTPS_ONLY,
)


@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    context: dict[str, Any] = Depends(get_template_context),
    task_service: TaskService = Depends(get_task_service),
    habit_service: HabitService = Depends(get_habit_service),
):
    tasks, _ = await task_service.list_tasks(
        per_page=5, theme_name=request.session.get("selected_theme")
    )
    habits, _ = await habit_service.list_habits(
        per_page=4,
        theme_name=request.session.get("selected_theme"),
        due_today_only=True,
    )
    context.update({"tasks": tasks, "habits": habits, "current_page": "home"})

    return templates.TemplateResponse(request, "index.html", context)


@app.get("/soon", response_class=HTMLResponse)
async def soon(
    request: Request, context: dict[str, Any] = Depends(get_template_context)
):
    context.update(
        {
            "request": request,
            "message": "Скоро",
            "details": "В разработке",
            "message_type": "info",
        }
    )
    return templates.TemplateResponse(request, "message.html", context)
