from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, date, datetime
import re
from uuid import UUID, uuid4

import pytest
from fastapi import Request
from httpx import ASGITransport, AsyncClient

from src.dependencies import (
    get_habit_service,
    get_user_habit_service,
    require_auth,
)
from src.csrf import require_csrf
from src.exceptions import HabitNotFound
from src.main import app
from src.schemas.auth import AuthUser
from src.schemas.habits import HabitCompletionResult
from src.utils import ensure_csrf_token, get_template_context

pytestmark = pytest.mark.asyncio


def _mk_user() -> AuthUser:
    now = datetime(2026, 3, 8, 12, 0, tzinfo=UTC)
    return AuthUser(
        id=uuid4(),
        email="habit-user@example.com",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


class _FakeHabitService:
    def __init__(
        self,
        *,
        exists: bool = True,
        create_error: Exception | None = None,
        update_error: Exception | None = None,
        update_returns_none: bool = False,
        complete_error: Exception | None = None,
        incomplete_error: Exception | None = None,
        delete_error: Exception | None = None,
    ):
        self.exists = exists
        self.create_error = create_error
        self.update_error = update_error
        self.update_returns_none = update_returns_none
        self.complete_error = complete_error
        self.incomplete_error = incomplete_error
        self.delete_error = delete_error

    async def list_habits(self, *args: object, **kwargs: object) -> tuple[list[object], int]:
        return ([], 0)

    async def create_habit(self, habit_data: object) -> object:
        if self.create_error:
            raise self.create_error
        return {"id": uuid4()}

    async def get_habit(self, habit_id: UUID) -> object | None:
        if not self.exists:
            return None
        return {"id": habit_id}

    async def update_habit(self, habit_id: UUID, habit_data: object) -> object | None:
        if self.update_error:
            raise self.update_error
        if self.update_returns_none:
            return None
        return {"id": habit_id}

    async def complete_habit(self, habit_id: UUID) -> HabitCompletionResult:
        if self.complete_error:
            raise self.complete_error
        if not self.exists:
            raise HabitNotFound
        return HabitCompletionResult(
            success=True,
            completed=True,
            date=date(2026, 3, 4),
            new_streak=4,
            changed=True,
        )

    async def incomplete_habit(self, habit_id: UUID) -> HabitCompletionResult:
        if self.incomplete_error:
            raise self.incomplete_error
        if not self.exists:
            raise HabitNotFound
        return HabitCompletionResult(
            success=True,
            completed=False,
            date=date(2026, 3, 4),
            new_streak=3,
            changed=True,
        )

    async def delete_habit(self, habit_id: UUID) -> bool:
        if self.delete_error:
            raise self.delete_error
        return True


def _override_habit_service(service: _FakeHabitService) -> None:
    app.dependency_overrides[get_habit_service] = lambda: service
    app.dependency_overrides[get_user_habit_service] = lambda: service


def _extract_csrf_token(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match is not None
    return match.group(1)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def fake_template_context(request: Request) -> dict[str, object]:
        return {
            "request": request,
            "themes": [],
            "stats": {"active_tasks": 0, "total_habits": 0, "success_rate": 0},
            "csrf_token": ensure_csrf_token(request),
        }

    app.dependency_overrides[get_template_context] = fake_template_context
    app.dependency_overrides[require_auth] = _mk_user
    app.dependency_overrides[require_csrf] = lambda: None
    _override_habit_service(_FakeHabitService())
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()


async def test_habits_list_returns_200_html(client: AsyncClient) -> None:
    res = await client.get("/habits/")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/html")


async def test_habits_new_returns_200_html(client: AsyncClient) -> None:
    res = await client.get("/habits/new")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/html")


async def test_habits_list_rejects_invalid_schedule_type_with_422(client: AsyncClient) -> None:
    res = await client.get("/habits/?schedule_type=invalid")
    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")


async def test_habits_list_rejects_legacy_all_status_with_422(client: AsyncClient) -> None:
    res = await client.get("/habits/?status=all")
    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")


async def test_habits_list_rejects_invalid_per_page_with_422(client: AsyncClient) -> None:
    res = await client.get("/habits/?per_page=0")
    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")


async def test_create_habit_returns_303_redirect_on_success(client: AsyncClient) -> None:
    page = await client.get("/habits/new")
    csrf_token = _extract_csrf_token(page.text)
    payload = {
        "name": "Утренняя зарядка",
        "schedule_type": "daily",
        "csrf_token": csrf_token,
    }
    res = await client.post("/habits/", data=payload, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/habits"


async def test_create_habit_rejects_missing_csrf_token_for_form(client: AsyncClient) -> None:
    app.dependency_overrides.pop(require_csrf, None)
    payload = {
        "name": "Утренняя зарядка",
        "schedule_type": "daily",
    }
    res = await client.post("/habits/", data=payload, follow_redirects=False)
    assert res.status_code == 403
    assert res.headers["content-type"].startswith("text/html")
    assert "Сессия формы истекла" in res.text


async def test_create_habit_rejects_missing_csrf_token_for_json(client: AsyncClient) -> None:
    app.dependency_overrides.pop(require_csrf, None)
    res = await client.post(
        "/habits/",
        json={"name": "Утренняя зарядка", "schedule_type": "daily"},
    )
    assert res.status_code == 403
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Invalid CSRF token"


async def test_create_habit_accepts_valid_csrf_token(client: AsyncClient) -> None:
    app.dependency_overrides.pop(require_csrf, None)
    page = await client.get("/habits/new")
    csrf_token = _extract_csrf_token(page.text)
    res = await client.post(
        "/habits/",
        data={
            "name": "Утренняя зарядка",
            "schedule_type": "daily",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )
    assert res.status_code == 303
    assert res.headers["location"] == "/habits"


async def test_get_habit_page_returns_404_when_missing(client: AsyncClient) -> None:
    _override_habit_service(_FakeHabitService(exists=False))
    res = await client.get(f"/habits/{uuid4()}")
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("text/html")


async def test_get_habit_page_rejects_invalid_uuid_with_422(client: AsyncClient) -> None:
    res = await client.get("/habits/not-a-uuid")
    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")


async def test_update_habit_returns_success_payload(client: AsyncClient) -> None:
    res = await client.put(
        f"/habits/{uuid4()}",
        json={"name": "Обновленная привычка", "schedule_type": "daily"},
    )
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    assert res.json() == {"message": "success"}


async def test_update_habit_returns_400_on_business_error(client: AsyncClient) -> None:
    _override_habit_service(_FakeHabitService(update_error=ValueError("bad update")))
    res = await client.put(
        f"/habits/{uuid4()}",
        json={"name": "Обновленная привычка"},
    )
    assert res.status_code == 400
    assert res.headers["content-type"].startswith("application/json")
    payload = res.json()
    assert payload["error"]["code"] == "bad_request"


async def test_update_habit_returns_404_when_missing(client: AsyncClient) -> None:
    _override_habit_service(_FakeHabitService(update_error=HabitNotFound()))
    res = await client.put(f"/habits/{uuid4()}", json={"name": "Missing"})
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")
    payload = res.json()
    assert payload["error"]["code"] == "not_found"


async def test_update_habit_rejects_invalid_uuid_with_422(client: AsyncClient) -> None:
    res = await client.put("/habits/not-a-uuid", json={"name": "Updated"})
    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")


async def test_complete_habit_returns_payload_when_ok(client: AsyncClient) -> None:
    res = await client.patch(f"/habits/{uuid4()}/complete")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    payload = res.json()
    assert payload["success"] is True
    assert payload["completed"] is True
    assert payload["date"] == "2026-03-04"
    assert isinstance(payload["new_streak"], int)
    assert isinstance(payload["changed"], bool)


async def test_complete_habit_returns_404_when_missing(client: AsyncClient) -> None:
    _override_habit_service(_FakeHabitService(exists=False))
    res = await client.patch(f"/habits/{uuid4()}/complete")
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")


async def test_complete_habit_rejects_missing_csrf_token(client: AsyncClient) -> None:
    app.dependency_overrides.pop(require_csrf, None)
    res = await client.patch(f"/habits/{uuid4()}/complete")
    assert res.status_code == 403
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "CSRF token is missing"


async def test_complete_habit_rejects_invalid_uuid_with_422(client: AsyncClient) -> None:
    res = await client.patch("/habits/not-a-uuid/complete")
    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")


async def test_complete_habit_returns_400_on_value_error(client: AsyncClient) -> None:
    _override_habit_service(_FakeHabitService(complete_error=ValueError("bad complete")))
    res = await client.patch(f"/habits/{uuid4()}/complete")
    assert res.status_code == 400
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "bad complete"


async def test_complete_habit_returns_500_on_runtime_error(client: AsyncClient) -> None:
    _override_habit_service(_FakeHabitService(complete_error=RuntimeError("boom")))
    res = await client.patch(f"/habits/{uuid4()}/complete")
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Internal server error"


async def test_incomplete_habit_returns_payload_when_ok(client: AsyncClient) -> None:
    res = await client.patch(f"/habits/{uuid4()}/incomplete")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    payload = res.json()
    assert payload["success"] is True
    assert payload["completed"] is False
    assert payload["date"] == "2026-03-04"
    assert isinstance(payload["new_streak"], int)
    assert isinstance(payload["changed"], bool)


async def test_incomplete_habit_returns_404_when_missing(client: AsyncClient) -> None:
    _override_habit_service(_FakeHabitService(exists=False))
    res = await client.patch(f"/habits/{uuid4()}/incomplete")
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")


async def test_incomplete_habit_rejects_invalid_uuid_with_422(client: AsyncClient) -> None:
    res = await client.patch("/habits/not-a-uuid/incomplete")
    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")


async def test_incomplete_habit_returns_400_on_value_error(client: AsyncClient) -> None:
    _override_habit_service(
        _FakeHabitService(incomplete_error=ValueError("bad incomplete"))
    )
    res = await client.patch(f"/habits/{uuid4()}/incomplete")
    assert res.status_code == 400
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "bad incomplete"


async def test_incomplete_habit_returns_500_on_runtime_error(client: AsyncClient) -> None:
    _override_habit_service(_FakeHabitService(incomplete_error=RuntimeError("boom")))
    res = await client.patch(f"/habits/{uuid4()}/incomplete")
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Internal server error"


async def test_delete_habit_returns_204_when_success(client: AsyncClient) -> None:
    res = await client.delete(f"/habits/{uuid4()}")
    assert res.status_code == 204


async def test_delete_habit_rejects_invalid_uuid_with_422(client: AsyncClient) -> None:
    res = await client.delete("/habits/not-a-uuid")
    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")
