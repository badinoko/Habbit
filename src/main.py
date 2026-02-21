from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.routers.tasks import router as tasks_router
from src.routers.themes import router as themes_router
from src.schemas.tasks import TaskResponse
from src.utils import get_list_tasks, get_template_context, templates

app = FastAPI(title="HabitFlow", description="Трекер привычек и задач", version="1.0.0")

app.mount("/static", StaticFiles(directory="src/static"), name="static")


app.include_router(themes_router)
app.include_router(tasks_router)

app.add_middleware(SessionMiddleware, secret_key="your-secret-key")


@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
    context: dict[str, Any] = Depends(get_template_context),
    tasks: list[TaskResponse] = Depends(get_list_tasks),
):
    context.update({"tasks": tasks, "habits": [], "current_page": "home"})

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
