from datetime import datetime
from typing import Literal
from uuid import UUID

from src.exceptions import TaskNotFound
from src.repositories import TaskRepository, ThemeRepository
from src.schemas import (
    TaskCreate,
    TaskCreateAPI,
    TaskInDB,
    TaskResponse,
    TaskStats,
    TaskUpdate,
    TaskUpdateAPI,
)

PRIORITY_IDS = {
    "low": UUID("00000000-0000-0000-0000-000000000001"),
    "medium": UUID("00000000-0000-0000-0000-000000000002"),
    "high": UUID("00000000-0000-0000-0000-000000000003"),
}

ID_TO_PRIORITY = {value: key for key, value in PRIORITY_IDS.items()}

# Доступные приоритеты согласно миграции "add_priorities_in_table"
PRIORITIES = {
    "low": {"name": "низкий", "weight": 1, "color": "#22C55E"},
    "medium": {"name": "средний", "weight": 2, "color": "#EAB308"},
    "high": {"name": "высокий", "weight": 3, "color": "#EF4444"},
}


Status = Literal["active", "completed", "all"]
Sort = Literal["created_at", "updated_at", "name", "priority"]
Order = Literal["asc", "desc"]


class TaskService:
    def __init__(self, task_repo: TaskRepository, theme_repo: ThemeRepository):
        self.task_repo = task_repo
        self.theme_repo = theme_repo

    async def create_task(self, task_data: TaskCreateAPI) -> TaskInDB:
        """Создать новую задачу"""
        if task_data.theme_id:
            theme = await self.theme_repo.get_by_id(task_data.theme_id)
            if not theme:
                raise ValueError("Theme not found")

        new_task_data = TaskCreate(
            name=task_data.name,
            description=task_data.description,
            theme_id=task_data.theme_id,
            priority_id=self.map_priority(task_data.priority),
        )

        return await self.task_repo.add(new_task_data)

    async def get_task(self, task_id: UUID) -> TaskInDB | None:
        """Получить задачу по ID"""
        return await self.task_repo.get_by_id(task_id)

    async def get_task_priorities(self) -> dict[str, dict[str, object]]:
        """Получить приоритеты"""
        return PRIORITIES

    async def get_priority(self, priority_id: UUID) -> str:
        return ID_TO_PRIORITY[priority_id]

    async def delete_task(self, task_id: UUID) -> bool:
        """Удалить задачу"""
        return await self.task_repo.delete(task_id)

    async def update_task(
        self, task_id: UUID, task_data: TaskUpdateAPI
    ) -> TaskInDB | None:
        """Обновить задачу"""
        old_task = await self.get_task(task_id)
        if not old_task:
            raise TaskNotFound

        # Получаем только явно переданные поля
        raw_data = task_data.model_dump(exclude_unset=True)
        if not raw_data:
            return old_task  # ничего не меняем

        update_dict = {}

        if "name" in raw_data:
            update_dict["name"] = raw_data["name"]
        if "description" in raw_data:
            update_dict["description"] = raw_data["description"]

        if "theme_id" in raw_data:
            theme_val = raw_data["theme_id"]
            if theme_val is not None:
                theme = await self.theme_repo.get_by_id(theme_val)
                if not theme:
                    raise ValueError("Theme not found")
            update_dict["theme_id"] = theme_val

        if "priority" in raw_data:
            update_dict["priority_id"] = self.map_priority(raw_data["priority"])

        updated_task = TaskUpdate(**update_dict)
        return await self.task_repo.update(task_id, updated_task)

    async def complete_task(self, task_id: UUID) -> TaskInDB | None:
        """Отметить задачу как выполненную"""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFound

        update_data = TaskUpdate(completed_at=datetime.now())
        return await self.task_repo.update(task_id, update_data)

    async def incomplete_task(self, task_id: UUID) -> TaskInDB | None:
        """Отметить задачу как невыполненную"""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise TaskNotFound

        update_data = TaskUpdate(completed_at=None)
        return await self.task_repo.update(task_id, update_data)

    async def list_tasks(
        self,
        page: int = 1,
        per_page: int = 20,
        theme_name: str | None = None,
        status: Status = "active",
        sort: Sort = "created_at",
        order: Order = "desc",
    ) -> tuple[list[TaskResponse], int]:
        skip = (page - 1) * per_page

        theme_id = None
        if theme_name:
            theme = await self.theme_repo.get_by_name(theme_name)
            if not theme:
                return ([], 0)
            theme_id = theme.id

        return await self.task_repo.list_tasks(
            skip=skip,
            limit=per_page,
            theme_id=theme_id,
            status=status,
            sort=sort,
            order=order,
        )

    async def get_task_statistics(self) -> TaskStats:
        """Получить статистику по задачам"""
        all_tasks = await self.task_repo.list()

        total = len(all_tasks)
        completed = 0
        pending = 0
        by_priority = dict.fromkeys(PRIORITIES, 0)
        by_theme = {}

        for task in all_tasks:
            if task.completed_at:
                completed += 1
            else:
                pending += 1

            if ID_TO_PRIORITY.get(task.priority_id) in by_priority:
                by_priority[ID_TO_PRIORITY[task.priority_id]] += 1

            theme_name = str(task.theme_id) if task.theme_id else "No theme"
            if theme_name not in by_theme:
                by_theme[theme_name] = 0
            by_theme[theme_name] += 1

        return TaskStats(
            total=total,
            completed=completed,
            pending=pending,
            by_priority=by_priority,
            by_theme=by_theme,
        )

    def map_priority(self, priority: str | UUID) -> UUID:
        if isinstance(priority, str):
            if priority not in PRIORITY_IDS:
                raise ValueError(f"Invalid priority: {priority}")
            return PRIORITY_IDS[priority]
        if isinstance(priority, UUID):
            if priority not in set(PRIORITY_IDS.values()):
                raise ValueError(f"Invalid priority UUID: {priority}")
            return priority
        raise ValueError("Priority must be str or UUID")
