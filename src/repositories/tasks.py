from uuid import UUID

from sqlalchemy import desc, select

from src.database.models import Priority, Task, Theme
from src.schemas import TaskCreate, TaskInDB, TaskUpdate
from src.schemas.tasks import TaskResponse

from .base import GenericSqlRepository


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

    async def get_by_status(self, is_completed: bool) -> list[TaskInDB]:
        """Получить задачи по статусу выполнения"""
        stmt = self._construct_list_stmt(is_completed=is_completed)
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

    async def get_completed_todos(self) -> list[TaskInDB]:
        """Получить выполненные задачи"""
        return await self.get_by_status(is_completed=True)

    async def get_pending_todos(self) -> list[TaskInDB]:
        """Получить невыполненные задачи"""
        return await self.get_by_status(is_completed=False)
