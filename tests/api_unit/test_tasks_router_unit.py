from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.dependencies import get_task_service
from src.exceptions import TaskNotFound
from src.main import app
from src.schemas.tasks import TaskInDB
from src.services.tasks import PRIORITY_IDS
from src.utils import get_template_context

pytestmark = pytest.mark.asyncio


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
    def __init__(
        self,
        *,
        exists: bool = True,
        complete_error: Exception | None = None,
        incomplete_error: Exception | None = None,
        create_error: Exception | None = None,
        create_returns_none: bool = False,
        update_error: Exception | None = None,
        update_returns_none: bool = False,
        delete_error: Exception | None = None,
    ):
        self.exists = exists
        self.complete_error = complete_error
        self.incomplete_error = incomplete_error
        self.create_error = create_error
        self.create_returns_none = create_returns_none
        self.update_error = update_error
        self.update_returns_none = update_returns_none
        self.delete_error = delete_error

    async def create_task(self, task_data):
        if self.create_error:
            raise self.create_error
        if self.create_returns_none:
            return None
        return _mk_task(uuid4())

    async def update_task(self, task_id: UUID, task_data):
        if self.update_error:
            raise self.update_error
        if self.update_returns_none:
            return None
        return _mk_task(task_id)

    async def delete_task(self, task_id: UUID) -> bool:
        if self.delete_error:
            raise self.delete_error
        return True

    async def complete_task(self, task_id: UUID) -> TaskInDB:
        if self.complete_error:
            raise self.complete_error
        if not self.exists:
            raise TaskNotFound
        return _mk_task(task_id).model_copy(update={"completed_at": datetime.now(UTC)})

    async def incomplete_task(self, task_id: UUID) -> TaskInDB:
        if self.incomplete_error:
            raise self.incomplete_error
        if not self.exists:
            raise TaskNotFound
        return _mk_task(task_id).model_copy(update={"completed_at": None})


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def fake_template_context():
        return {
            "themes": [],
            "stats": {"active_tasks": 0, "total_habits": 0, "success_rate": 0},
        }

    app.dependency_overrides[get_template_context] = fake_template_context
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()


async def test_complete_task_returns_404_when_missing(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(exists=False)
    res = await client.patch(f"/tasks/{uuid4()}/complete")
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")


async def test_complete_task_returns_payload_when_ok(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(exists=True)
    task_id = uuid4()
    res = await client.patch(f"/tasks/{task_id}/complete")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    payload = res.json()
    assert payload["success"] is True
    assert payload["completed"] is True
    assert payload["task"]["id"] == str(task_id)


async def test_incomplete_task_returns_404_when_missing(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(exists=False)
    res = await client.patch(f"/tasks/{uuid4()}/incomplete")
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")


async def test_incomplete_task_returns_payload_when_ok(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(exists=True)
    task_id = uuid4()
    res = await client.patch(f"/tasks/{task_id}/incomplete")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    payload = res.json()
    assert payload["success"] is True
    assert payload["completed"] is False
    assert payload["task"]["id"] == str(task_id)


async def test_complete_task_returns_500_on_unexpected_error(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        complete_error=RuntimeError("boom")
    )
    res = await client.patch(f"/tasks/{uuid4()}/complete")
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Internal server error"


async def test_incomplete_task_returns_500_on_unexpected_error(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        incomplete_error=RuntimeError("boom")
    )
    res = await client.patch(f"/tasks/{uuid4()}/incomplete")
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Internal server error"


async def test_create_task_returns_redirect_on_success(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService()
    res = await client.post(
        "/tasks/",
        data={"name": "Task", "priority": "low"},
        follow_redirects=False,
    )
    assert res.status_code == 303
    assert res.headers["location"] == "/tasks"


async def test_create_task_returns_400_on_value_error(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        create_error=ValueError("bad task")
    )
    res = await client.post("/tasks/", data={"name": "Task", "priority": "low"})
    assert res.status_code == 400
    assert res.headers["content-type"].startswith("text/html")
    assert "bad task" in res.text


async def test_create_task_returns_500_on_runtime_error(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        create_error=RuntimeError("broken")
    )
    res = await client.post("/tasks/", data={"name": "Task", "priority": "low"})
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("text/html")
    assert "broken" in res.text


async def test_create_task_returns_500_when_service_returns_none(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        create_returns_none=True
    )
    res = await client.post("/tasks/", data={"name": "Task", "priority": "low"})
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("text/html")
    assert "Задача не создана" in res.text


async def test_update_task_returns_success_payload(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService()
    res = await client.put(f"/tasks/{uuid4()}", json={"name": "Updated"})
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    assert res.json() == {"message": "success"}


async def test_update_task_returns_400_on_value_error(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        update_error=ValueError("bad update")
    )
    res = await client.put(f"/tasks/{uuid4()}", json={"name": "Updated"})
    assert res.status_code == 400
    assert res.headers["content-type"].startswith("application/json")
    assert res.json() == {
        "error": {"code": "bad_request", "message": "bad update"}
    }


async def test_update_task_returns_404_on_task_not_found(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        update_error=TaskNotFound()
    )
    res = await client.put(f"/tasks/{uuid4()}", json={"name": "Updated"})
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")
    assert res.json() == {
        "error": {"code": "not_found", "message": "Задача не найдена"}
    }


async def test_update_task_returns_500_on_runtime_error(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        update_error=RuntimeError("failed update")
    )
    res = await client.put(f"/tasks/{uuid4()}", json={"name": "Updated"})
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("application/json")
    assert res.json() == {
        "error": {"code": "internal_error", "message": "Internal server error"}
    }


async def test_update_task_returns_500_when_service_returns_none(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        update_returns_none=True
    )
    res = await client.put(f"/tasks/{uuid4()}", json={"name": "Updated"})
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("application/json")
    assert res.json() == {
        "error": {"code": "internal_error", "message": "Задача не обновлена"}
    }


async def test_delete_task_returns_204_when_success(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService()
    res = await client.delete(f"/tasks/{uuid4()}")
    assert res.status_code == 204


async def test_delete_task_returns_500_when_runtime_error(client):
    app.dependency_overrides[get_task_service] = lambda: _FakeTaskService(
        delete_error=RuntimeError("cannot delete")
    )
    res = await client.delete(f"/tasks/{uuid4()}")
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Internal server error"
