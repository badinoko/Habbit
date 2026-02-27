from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.dependencies import get_task_service
from src.exceptions import TaskNotFound
from src.main import app
from src.schemas.tasks import TaskInDB
from src.services.tasks import PRIORITY_IDS


def _mk_task(task_id: UUID) -> TaskInDB:
    now = datetime(2026, 1, 1, 0, 0, 0)
    return TaskInDB(
        id=task_id,
        name="t",
        description=None,
        theme_id=None,
        priority_id=PRIORITY_IDS["low"],
        completed_at=None,
        created_at=now,
        updated_at=now,
    )


class _FakeTaskService:
    def __init__(self, *, exists: bool):
        self.exists = exists

    async def complete_task(self, task_id: UUID) -> TaskInDB:
        if not self.exists:
            raise TaskNotFound
        return _mk_task(task_id).model_copy(update={"completed_at": datetime.now()})

    async def incomplete_task(self, task_id: UUID) -> TaskInDB:
        if not self.exists:
            raise TaskNotFound
        return _mk_task(task_id).model_copy(update={"completed_at": None})


@pytest.fixture
def client():
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


def test_complete_task_returns_404_when_missing(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(exists=False)
    res = client.patch(f"/tasks/{uuid4()}/complete")
    assert res.status_code == 404


def test_complete_task_returns_payload_when_ok(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(exists=True)
    task_id = uuid4()
    res = client.patch(f"/tasks/{task_id}/complete")
    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["completed"] is True
    assert payload["task"]["id"] == str(task_id)
