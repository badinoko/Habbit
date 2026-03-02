from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

import pytest

from src.exceptions import TaskNotFound
from src.schemas.tasks import TaskCreateAPI, TaskInDB, TaskResponse, TaskUpdateAPI
from src.services.tasks import PRIORITY_IDS, TaskService


class DummyTaskRepo:
    """
    Minimal stub of TaskRepository for TaskService tests.

    Tests configure attributes directly to describe the behavior they need.
    """

    def __init__(self) -> None:
        self.get_by_id_result: TaskInDB | None = None
        self.list_result: list[TaskInDB] = []
        self.list_tasks_result: tuple[list[TaskResponse], int] = ([], 0)
        self.list_tasks_last_kwargs: dict[str, object] | None = None
        self.updated_called: bool = False

    async def add(self, data):
        return TaskInDB(
            id=uuid4(),
            name=data.name,
            description=data.description,
            theme_id=data.theme_id,
            priority_id=data.priority_id,
            completed_at=None,
            created_at=datetime(2026, 1, 1, 0, 0, 0),
            updated_at=datetime(2026, 1, 1, 0, 0, 0),
        )

    async def get_by_id(self, task_id: UUID) -> TaskInDB | None:
        return self.get_by_id_result

    async def update(self, task_id: UUID, data):
        self.updated_called = True
        if self.get_by_id_result is None:
            return None
        dump = data.model_dump(exclude_unset=True)
        self.get_by_id_result = self.get_by_id_result.model_copy(update=dump)
        return self.get_by_id_result

    async def delete(self, task_id: UUID) -> bool:
        return True

    async def list(self, *args: object, **kwargs: object) -> list[TaskInDB]:
        return list(self.list_result)

    async def list_tasks(self, **kwargs: object) -> tuple[list[TaskResponse], int]:
        self.list_tasks_last_kwargs = kwargs
        return self.list_tasks_result

    async def get_recent_for_dashboard(
        self, *args: object, **kwargs: object
    ) -> list[TaskInDB]:
        return []


class DummyThemeRepo:
    def __init__(self) -> None:
        self.get_by_id_result = None
        self.get_by_name_result = None

    async def get_by_id(self, theme_id: UUID):
        return self.get_by_id_result

    async def get_by_name(self, name: str):
        return self.get_by_name_result


def _mk_task(
    *,
    priority_id: UUID,
    completed_at: datetime | None,
    theme_id: UUID | None,
) -> TaskInDB:
    now = datetime(2026, 1, 1, 0, 0, 0)
    return TaskInDB(
        id=uuid4(),
        name="t",
        description=None,
        theme_id=theme_id,
        priority_id=priority_id,
        completed_at=completed_at,
        created_at=now,
        updated_at=now,
    )


def _mk_task_response(
    *,
    name: str = "t",
    priority: str = "low",
    completed_at: datetime | None = None,
    theme_name: str | None = None,
    theme_color: str | None = None,
    theme_id: UUID | None = None,
) -> TaskResponse:
    now = datetime(2026, 1, 1, 0, 0, 0)
    return TaskResponse(
        id=uuid4(),
        name=name,
        description=None,
        theme_id=theme_id,
        priority=priority,
        theme_name=theme_name,
        theme_color=theme_color,
        completed_at=completed_at,
        created_at=now,
        updated_at=now,
    )


class _ThemeObj:
    def __init__(self, theme_id: UUID) -> None:
        self.id = theme_id


@pytest.mark.asyncio
async def test_map_priority_accepts_str_and_uuid():
    task_repo = DummyTaskRepo()
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    assert service.map_priority("low") == PRIORITY_IDS["low"]
    assert service.map_priority(PRIORITY_IDS["high"]) == PRIORITY_IDS["high"]


def test_map_priority_rejects_invalid_str():
    task_repo = DummyTaskRepo()
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    with pytest.raises(ValueError, match="Invalid priority"):
        service.map_priority("urgent")


def test_map_priority_rejects_invalid_uuid():
    task_repo = DummyTaskRepo()
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    with pytest.raises(ValueError, match="Invalid priority UUID"):
        service.map_priority(uuid4())


def test_map_priority_rejects_invalid_type():
    task_repo = DummyTaskRepo()
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    with pytest.raises(ValueError, match="Priority must be str or UUID"):
        service.map_priority(123)


@pytest.mark.asyncio
async def test_create_task_validates_theme_exists_when_theme_id_set():
    task_repo = DummyTaskRepo()
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    data = TaskCreateAPI(name="n", priority="low", theme_id=uuid4())
    with pytest.raises(ValueError, match="Theme not found"):
        await service.create_task(data)


@pytest.mark.asyncio
async def test_update_task_raises_when_task_missing():
    task_repo = DummyTaskRepo()
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    with pytest.raises(TaskNotFound):
        await service.update_task(uuid4(), TaskUpdateAPI(name="x"))


@pytest.mark.asyncio
async def test_update_task_returns_old_when_no_fields_set():
    task_id = uuid4()
    existing_task = _mk_task(
        priority_id=PRIORITY_IDS["low"], completed_at=None, theme_id=None
    ).model_copy(update={"id": task_id})

    task_repo = DummyTaskRepo()
    task_repo.get_by_id_result = existing_task
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    res = await service.update_task(task_id, TaskUpdateAPI())
    assert res == existing_task
    assert task_repo.updated_called is False


@pytest.mark.asyncio
async def test_update_task_validates_theme_and_maps_priority():
    task_id = uuid4()
    theme_id = uuid4()
    existing_task = _mk_task(
        priority_id=PRIORITY_IDS["low"], completed_at=None, theme_id=None
    ).model_copy(update={"id": task_id})

    task_repo = DummyTaskRepo()
    task_repo.get_by_id_result = existing_task
    theme_repo = DummyThemeRepo()
    theme_repo.get_by_id_result = object()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    res = await service.update_task(
        task_id, TaskUpdateAPI(priority="high", theme_id=theme_id)
    )
    assert res is not None
    assert res.priority_id == PRIORITY_IDS["high"]
    assert res.theme_id == theme_id


@pytest.mark.asyncio
async def test_complete_task_raises_when_missing():
    task_repo = DummyTaskRepo()
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    with pytest.raises(TaskNotFound):
        await service.complete_task(uuid4())


@pytest.mark.asyncio
async def test_complete_task_sets_completed_at():
    task_id = uuid4()
    existing = _mk_task(
        priority_id=PRIORITY_IDS["low"], completed_at=None, theme_id=None
    ).model_copy(update={"id": task_id})

    task_repo = DummyTaskRepo()
    task_repo.get_by_id_result = existing
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    res = await service.complete_task(task_id)
    assert res is not None
    assert res.completed_at is not None


@pytest.mark.asyncio
async def test_incomplete_task_raises_when_missing():
    task_repo = DummyTaskRepo()
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    with pytest.raises(TaskNotFound):
        await service.incomplete_task(uuid4())


@pytest.mark.asyncio
async def test_incomplete_task_clears_completed_at():
    task_id = uuid4()
    existing = _mk_task(
        priority_id=PRIORITY_IDS["low"],
        completed_at=datetime(2026, 1, 1, 0, 0, 0),
        theme_id=None,
    ).model_copy(update={"id": task_id})

    task_repo = DummyTaskRepo()
    task_repo.get_by_id_result = existing
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    res = await service.incomplete_task(task_id)
    assert res is not None
    assert res.completed_at is None


@pytest.mark.asyncio
async def test_list_tasks_returns_empty_when_theme_not_found():
    task_repo = DummyTaskRepo()
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    res = await service.list_tasks(theme_name="Missing")
    assert res == ([], 0)
    assert task_repo.list_tasks_last_kwargs is None


@pytest.mark.asyncio
async def test_list_tasks_passes_filters_to_repo():
    theme_id = uuid4()
    task_repo = DummyTaskRepo()
    task_repo.list_tasks_result = (
        [
            _mk_task_response(
                name="z",
                priority="high",
                theme_name="Work",
                theme_color="#123456",
                theme_id=theme_id,
            )
        ],
        1,
    )
    theme_repo = DummyThemeRepo()
    theme_repo.get_by_name_result = _ThemeObj(theme_id)
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    res = await service.list_tasks(
        page=2,
        per_page=5,
        theme_name="Work",
        status="completed",
        sort="name",
        order="asc",
    )

    assert res == task_repo.list_tasks_result
    assert task_repo.list_tasks_last_kwargs == {
        "skip": 5,
        "limit": 5,
        "theme_id": theme_id,
        "status": "completed",
        "sort": "name",
        "order": "asc",
    }


@pytest.mark.asyncio
async def test_get_task_statistics_counts_and_groups():
    task_repo = DummyTaskRepo()
    task_repo.list_result = [
        _mk_task(priority_id=PRIORITY_IDS["low"], completed_at=None, theme_id=None),
        _mk_task(
            priority_id=PRIORITY_IDS["low"],
            completed_at=datetime(2026, 1, 1, 0, 0, 0),
            theme_id=uuid4(),
        ),
        _mk_task(priority_id=PRIORITY_IDS["high"], completed_at=None, theme_id=None),
    ]
    theme_repo = DummyThemeRepo()
    service = TaskService(task_repo=task_repo, theme_repo=theme_repo)

    stats = await service.get_task_statistics()
    assert stats.total == 3
    assert stats.completed == 1
    assert stats.pending == 2
    assert stats.by_priority["low"] == 2
    assert stats.by_priority["high"] == 1
    assert stats.by_priority["medium"] == 0
    assert stats.by_theme["No theme"] == 2
