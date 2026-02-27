from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.dependencies import get_theme_service
from src.main import app
from src.schemas.themes import ThemeInDB, ThemeUpdate


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
    def __init__(self, *, exists: bool):
        self.exists = exists

    async def get_theme_by_name(self, name: str):
        if not self.exists:
            return None
        return _mk_theme(name, "#FF00FF")

    async def update_theme(self, old_theme: ThemeInDB, theme_data: ThemeUpdate):
        dump = theme_data.model_dump(exclude_unset=True)
        return old_theme.model_copy(update=dump)

    async def delete_theme(self, theme: str) -> None:
        return None


@pytest.fixture
def client():
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


def test_update_theme_returns_404_when_missing(client):
    app.dependency_overrides[get_theme_service] = lambda: _FakeThemeService(
        exists=False
    )
    res = client.put("/themes/Nope", json={"name": "X"})
    assert res.status_code == 404


def test_update_theme_returns_success_payload(client):
    app.dependency_overrides[get_theme_service] = lambda: _FakeThemeService(exists=True)
    res = client.put("/themes/Hobby", json={"color": "#FFFFFF"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["theme"]["name"] == "Hobby"
    assert data["theme"]["color"] == "#FFFFFF"
