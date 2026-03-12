from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import Request
from httpx import ASGITransport, AsyncClient

from src.dependencies import (
    get_theme_service,
    get_user_theme_service,
    require_auth,
)
from src.csrf import require_csrf
from src.main import app
from src.schemas.themes import ThemeCreate, ThemeInDB, ThemeUpdate
from src.utils import ensure_csrf_token, get_template_context
from tests.helpers import extract_csrf_token, make_auth_user

pytestmark = pytest.mark.asyncio


def _mk_theme(name: str, color: str) -> ThemeInDB:
    now = datetime(2026, 1, 1, 0, 0, 0)
    return ThemeInDB(
        id=uuid4(),
        name=name,
        color=color,
        created_at=now,
        updated_at=now,
    )


class _FakeThemeService:
    def __init__(
        self,
        *,
        exists: bool = True,
        create_error: Exception | None = None,
        create_returns_none: bool = False,
        update_error: Exception | None = None,
        update_returns_none: bool = False,
        themes_count: int = 0,
    ):
        self.exists = exists
        self.create_error = create_error
        self.create_returns_none = create_returns_none
        self.update_error = update_error
        self.update_returns_none = update_returns_none
        self.themes_count = themes_count

    async def list_themes_with_counts(
        self, page: int = 1, per_page: int = 20
    ) -> tuple[list[ThemeInDB], int]:
        return ([], self.themes_count)

    async def get_existing_colors(self) -> set[str]:
        return set()

    async def create_theme(self, theme_data: ThemeCreate):
        if self.create_error:
            raise self.create_error
        if self.create_returns_none:
            return None
        return _mk_theme(theme_data.name, theme_data.color or "#FF00FF")

    async def get_theme_by_name(self, name: str):
        if not self.exists:
            return None
        return _mk_theme(name, "#FF00FF")

    async def update_theme(self, old_theme: ThemeInDB, theme_data: ThemeUpdate):
        if self.update_error:
            raise self.update_error
        if self.update_returns_none:
            return None
        dump = theme_data.model_dump(exclude_unset=True)
        return old_theme.model_copy(update=dump)

    async def delete_theme(self, theme: str) -> None:
        return None


def _override_theme_service(service: _FakeThemeService) -> None:
    app.dependency_overrides[get_theme_service] = lambda: service
    app.dependency_overrides[get_user_theme_service] = lambda: service

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def fake_template_context(request: Request):
        return {
            "request": request,
            "themes": [],
            "stats": {"active_tasks": 0, "total_habits": 0, "success_rate": 0},
            "csrf_token": ensure_csrf_token(request),
        }

    app.dependency_overrides[get_template_context] = fake_template_context
    app.dependency_overrides[require_auth] = lambda: make_auth_user(
        "theme-user@example.com"
    )
    app.dependency_overrides[require_csrf] = lambda: None
    _override_theme_service(_FakeThemeService())
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()


async def test_update_theme_returns_404_when_missing(client):
    _override_theme_service(_FakeThemeService(exists=False))
    res = await client.put("/themes/Nope", json={"name": "X"})
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")


async def test_update_theme_returns_success_payload(client):
    _override_theme_service(_FakeThemeService(exists=True))
    res = await client.put("/themes/Hobby", json={"color": "#FFFFFF"})
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    data = res.json()
    assert data["status"] == "success"
    assert data["theme"]["name"] == "Hobby"
    assert data["theme"]["color"] == "#FFFFFF"


async def test_update_theme_returns_400_on_value_error(client):
    _override_theme_service(
        _FakeThemeService(update_error=ValueError("Theme with this name already exists"))
    )
    res = await client.put("/themes/Hobby", json={"name": "Work"})
    assert res.status_code == 400
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Theme with this name already exists"


async def test_create_theme_returns_redirect_on_success(client):
    _override_theme_service(_FakeThemeService())
    page = await client.get("/themes/new")
    csrf_token = extract_csrf_token(page.text)
    res = await client.post(
        "/themes/",
        data={"name": "Hobby", "csrf_token": csrf_token},
        follow_redirects=False,
    )
    assert res.status_code == 303
    assert res.headers["location"] == "/themes"


async def test_create_theme_returns_400_on_value_error(client):
    _override_theme_service(_FakeThemeService(create_error=ValueError("duplicate")))
    page = await client.get("/themes/new")
    csrf_token = extract_csrf_token(page.text)
    res = await client.post(
        "/themes/",
        data={"name": "Hobby", "csrf_token": csrf_token},
    )
    assert res.status_code == 400
    assert res.headers["content-type"].startswith("text/html")
    assert "duplicate" in res.text


async def test_create_theme_returns_500_on_runtime_error(client):
    _override_theme_service(_FakeThemeService(create_error=RuntimeError("unexpected")))
    page = await client.get("/themes/new")
    csrf_token = extract_csrf_token(page.text)
    res = await client.post(
        "/themes/",
        data={"name": "Hobby", "csrf_token": csrf_token},
    )
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("text/html")
    assert "unexpected" in res.text


async def test_create_theme_returns_500_when_service_returns_none(client):
    _override_theme_service(_FakeThemeService(create_returns_none=True))
    page = await client.get("/themes/new")
    csrf_token = extract_csrf_token(page.text)
    res = await client.post(
        "/themes/",
        data={"name": "Hobby", "csrf_token": csrf_token},
    )
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("text/html")
    assert "Тема не создана" in res.text


async def test_create_theme_rejects_missing_csrf_token(client):
    app.dependency_overrides.pop(require_csrf, None)
    res = await client.post("/themes/", data={"name": "Hobby"})
    assert res.status_code == 403
    assert res.headers["content-type"].startswith("text/html")
    assert "Сессия формы истекла" in res.text


async def test_create_theme_accepts_valid_csrf_token(client):
    app.dependency_overrides.pop(require_csrf, None)
    page = await client.get("/themes/new")
    csrf_token = extract_csrf_token(page.text)
    res = await client.post(
        "/themes/",
        data={"name": "Hobby", "csrf_token": csrf_token},
        follow_redirects=False,
    )
    assert res.status_code == 303
    assert res.headers["location"] == "/themes"


async def test_get_theme_page_returns_404_when_missing(client):
    _override_theme_service(_FakeThemeService(exists=False))
    res = await client.get("/themes/Missing")
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("text/html")


async def test_update_theme_returns_500_when_service_returns_none(client):
    _override_theme_service(_FakeThemeService(update_returns_none=True))
    res = await client.put("/themes/Hobby", json={"color": "#FFFFFF"})
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "Internal server error"


async def test_update_theme_rejects_missing_csrf_token(client):
    app.dependency_overrides.pop(require_csrf, None)
    res = await client.put("/themes/Hobby", json={"color": "#FFFFFF"})
    assert res.status_code == 403
    assert res.headers["content-type"].startswith("application/json")
    assert res.json()["detail"] == "CSRF token is missing"


async def test_get_themes_redirects_to_first_page_when_no_items(client):
    _override_theme_service(_FakeThemeService(themes_count=0))
    res = await client.get("/themes/?page=3&per_page=5", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == "/themes/?per_page=5"


async def test_get_themes_redirects_to_last_page_when_page_is_too_high(client):
    _override_theme_service(_FakeThemeService(themes_count=3))
    res = await client.get("/themes/?page=9&per_page=2", follow_redirects=False)
    assert res.status_code == 302
    assert res.headers["location"] == "/themes/?page=2&per_page=2"
