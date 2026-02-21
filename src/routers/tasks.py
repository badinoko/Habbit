from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from src.dependencies import get_task_service
from src.exceptions import TaskNotFound
from src.schemas import Response
from src.schemas.tasks import (
    TaskCreateAPI,
    TaskMarkCompleted,
    TaskResponse,
    TaskUpdateAPI,
)
from src.services import TaskService
from src.utils import get_list_tasks, get_template_context, templates

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "/",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Returns tasks page",
)
async def tasks_page(
    request: Request,
    context: dict[str, Any] = Depends(get_template_context),
    tasks: list[TaskResponse] = Depends(get_list_tasks),
):
    context.update({"tasks": tasks, "current_page": "tasks"})
    return templates.TemplateResponse(request, "tasks/tasks_list.html", context)


@router.get(
    "/new",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Returns task creation page",
)
async def create_task_page(
    request: Request,
    context: dict[str, Any] = Depends(get_template_context),
    service: TaskService = Depends(get_task_service),
):
    context.update(
        {
            "current_page": "tasks",
            "priorities": await service.get_task_priorities(),
            "task": {},  # Empty task object for the form
        }
    )
    return templates.TemplateResponse(request, "tasks/tasks_form.html", context)


@router.get(
    "/{task_id}",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Returns task edition page",
)
async def task_page(
    request: Request,
    task_id: UUID,
    context: dict[str, Any] = Depends(get_template_context),
    service: TaskService = Depends(get_task_service),
):
    task = await service.get_task(task_id)
    if not task:
        context = error_context_updater(context, "Задача не найдена")
        return templates.TemplateResponse(request, "message.html", context)
    priority = await service.get_priority(task.priority_id)  # Getting priority NAME
    context.update(
        {
            "current_page": "tasks",
            "priorities": await service.get_task_priorities(),
            "task": {
                "id": task_id,
                "name": task.name,
                "description": task.description,
                "theme_id": task.theme_id,
                "priority": priority,
            },
        }
    )
    return templates.TemplateResponse(request, "tasks/tasks_form.html", context)


@router.post(
    "/",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    summary="Creates new task and redirects to tasks list",
    responses={
        303: {"description": "Redirect to tasks list"},
        400: {"description": "Bad request - validation error"},
        500: {"description": "Internal server error"},
    },
)
async def create_task(
    request: Request,
    task_data: Annotated[TaskCreateAPI, Form()],
    context: dict[str, Any] = Depends(get_template_context),
    service: TaskService = Depends(get_task_service),
):
    try:
        res = await service.create_task(task_data)
        if not res:
            context = error_context_updater(context, "Задача не создана")
            return templates.TemplateResponse(
                request,
                "message.html",
                context,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return RedirectResponse(url="/tasks", status_code=status.HTTP_303_SEE_OTHER)
    except ValueError as e:
        context = error_context_updater(context, str(e))
        return templates.TemplateResponse(
            request, "message.html", context, status_code=status.HTTP_400_BAD_REQUEST
        )
    except RuntimeError as e:
        context = error_context_updater(context, str(e))
        return templates.TemplateResponse(
            request,
            "message.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes Task",
)
async def delete_task(task_id: UUID, service: TaskService = Depends(get_task_service)):
    try:
        await service.delete_task(task_id)
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


@router.patch(
    "/{id}/complete",
    summary="Marks task as completed",
    response_model=TaskMarkCompleted,
    responses={
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"},
    },
)
async def complete_task(id: UUID, service: TaskService = Depends(get_task_service)):
    try:
        res = await service.complete_task(id)
        return TaskMarkCompleted(success=True, completed=True, task=res)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Task not found") from None
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.patch(
    "/{id}/incomplete",
    summary="Marks task as incompleted",
    response_model=TaskMarkCompleted,
    responses={
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"},
    },
)
async def incomplete_task(id: UUID, service: TaskService = Depends(get_task_service)):
    try:
        res = await service.incomplete_task(id)
        return TaskMarkCompleted(success=True, completed=False, task=res)
    except TaskNotFound:
        raise HTTPException(status_code=404, detail="Task not found") from None
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.put(
    "/{id}/edit",
    response_model=Response,
    summary="Updates task",
    responses={
        404: {"description": "Task not found"},
    },
)
async def update_task(
    request: Request,
    id: UUID,
    task_data: TaskUpdateAPI,
    context: dict[str, Any] = Depends(get_template_context),
    service: TaskService = Depends(get_task_service),
):
    try:
        res = await service.update_task(id, task_data)
        if not res:
            context = error_context_updater(context, "Задача не обновлена")
            return templates.TemplateResponse(
                request,
                "message.html",
                context,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(message="success")
    except ValueError as e:
        context = error_context_updater(context, str(e))
        return templates.TemplateResponse(
            request, "message.html", context, status_code=status.HTTP_400_BAD_REQUEST
        )
    except RuntimeError as e:
        context = error_context_updater(context, str(e))
        return templates.TemplateResponse(
            request,
            "message.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def error_context_updater(context: dict[Any, Any], e: str):
    context.update({"message_type": "error", "title": "Ошибка", "message": str(e)})
    return context
