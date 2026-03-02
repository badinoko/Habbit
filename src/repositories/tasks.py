from typing import Any, Literal
from uuid import UUID

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.elements import SQLColumnExpression

from src.database.models import Priority, Task, Theme
from src.schemas import TaskCreate, TaskInDB, TaskUpdate
from src.schemas.tasks import TaskResponse

from .base import GenericSqlRepository

Status = Literal["active", "completed", "all"]
Sort = Literal["created_at", "updated_at", "name", "priority"]
Order = Literal["asc", "desc"]


class TaskRepository(
    GenericSqlRepository[TaskCreate, TaskInDB, TaskUpdate, Task, UUID]
):
    """
    Репозиторий для работы с задачами
    """

    _model = Task
    _create_schema = TaskCreate
    _read_schema = TaskInDB
    _update_schema = TaskUpdate

    async def get_by_theme_id(self, theme_id: UUID) -> list[TaskInDB]:
        """Получить задачи по ID темы"""
        stmt = self._construct_list_stmt(theme_id=theme_id)
        result = await self._session.execute(stmt)
        todos = result.scalars().all()
        return [self._convert_model_to_read(todo) for todo in todos]

    async def get_recent_for_dashboard(
        self, theme_name: str | None, completed: bool, limit: int = 5
    ) -> list[TaskResponse]:
        """
        Получить последние задачи для главной страницы
        """
        stmt = (
            select(Task, Priority, Theme)
            .join(Priority, Task.priority_id == Priority.id)
            .outerjoin(Theme, Task.theme_id == Theme.id)
        )

        if theme_name is not None:
            stmt = stmt.filter(Theme.name == theme_name)

        if not completed:
            stmt = stmt.filter(Task.completed_at.is_(None))

        stmt = stmt.order_by(desc(Task.created_at)).limit(limit)
        result = await self._session.execute(stmt)
        rows = result.all()
        tasks_for_dashboard = []
        priority_map = {"высокий": "high", "средний": "medium", "низкий": "low"}
        for task, priority, theme in rows:
            priority_en = priority_map[priority.name.lower()]
            tasks_for_dashboard.append(
                TaskResponse(
                    id=task.id,
                    name=task.name,
                    description=task.description,
                    completed_at=task.completed_at,
                    priority=priority_en,
                    theme_name=theme.name if theme else None,
                    theme_color=theme.color if theme else None,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
            )

        return tasks_for_dashboard

    async def list_tasks(
        self,
        skip: int,
        limit: int,
        theme_id: UUID | None,
        status: Status,
        sort: Sort,
        order: Order,
    ) -> tuple[list[TaskResponse], int]:
        stmt = select(Task).options(
            joinedload(Task.theme),
            joinedload(Task.priority),
        )

        if theme_id:
            stmt = stmt.where(Task.theme_id == theme_id)

        if status == "active":
            stmt = stmt.where(Task.completed_at.is_(None))
        elif status == "completed":
            stmt = stmt.where(Task.completed_at.is_not(None))

        count_stmt = select(func.count()).select_from(
            stmt.with_only_columns(Task.id).order_by(None).subquery()
        )
        total = await self._session.scalar(count_stmt)  # int

        order_fn = desc if order == "desc" else asc
        sort_col: SQLColumnExpression[Any]

        if sort == "priority":
            stmt = stmt.join(Task.priority)
            sort_col = Priority.weight
        elif sort == "updated_at":
            sort_col = Task.updated_at
        elif sort == "name":
            sort_col = Task.name
        else:
            sort_col = Task.created_at

        stmt = stmt.order_by(order_fn(sort_col), order_fn(Task.created_at))
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        records = result.scalars().unique().all()

        priority_map = {"высокий": "high", "средний": "medium", "низкий": "low"}

        items = [
            TaskResponse(
                id=task.id,
                name=task.name,
                description=task.description,
                completed_at=task.completed_at,
                priority=priority_map.get(
                    task.priority.name.strip().lower(), task.priority.name
                ),
                theme_name=task.theme.name if task.theme else None,
                theme_color=task.theme.color if task.theme else None,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
            for task in records
        ]

        return items, int(total or 0)
