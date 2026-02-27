from __future__ import annotations

from uuid import uuid4

import pytest

from src.schemas.themes import ThemeCreate, ThemeInDB, ThemeUpdate
from src.services.themes import ThemeService, string_to_hex


class DummyThemeRepo:
    """
    Minimal stub of ThemeRepository for ThemeService tests.

    Each test sets the attributes directly to describe the behavior it needs.
    """

    def __init__(self) -> None:
        self.get_by_name_result: ThemeInDB | None = None
        self.get_by_color_result: ThemeInDB | None = None
        self.add_return: ThemeInDB | None = None
        self.update_return: ThemeInDB | None = None
        self.update_called: bool = False

    async def get_by_name(self, name: str) -> ThemeInDB | None:
        return self.get_by_name_result

    async def get_by_color(self, color: str) -> ThemeInDB | None:
        return self.get_by_color_result

    async def add(self, data: ThemeCreate) -> ThemeInDB:
        if self.add_return is not None:
            return self.add_return
        return ThemeInDB(
            id=uuid4(),
            name=data.name,
            color=data.color or "#FFFFFF",
            created_at=_dt(2026, 1, 1),
            updated_at=_dt(2026, 1, 1),
        )

    async def update(self, theme_id, data: ThemeUpdate) -> ThemeInDB | None:  # type: ignore[no-untyped-def]
        self.update_called = True
        if self.update_return is not None:
            return self.update_return
        # Basic "echo" behavior: pretend we updated and return a merged object.
        base = self.get_by_name_result
        if base is None:
            return None
        dump = data.model_dump(exclude_unset=True)
        return base.model_copy(update=dump)

    async def delete(self, theme_id):  # type: ignore[no-untyped-def]
        return None

    async def list(self, *args: object, **kwargs: object) -> list[ThemeInDB]:
        return []

    async def list_with_task_counts(
        self, *args: object, **kwargs: object
    ) -> list[tuple[ThemeInDB, int]]:
        return []

    async def get_existing_colors_list(
        self, *args: object, **kwargs: object
    ) -> set[str]:
        if self.get_by_color_result is None:
            return set()
        return {self.get_by_color_result.color}


def _dt(y: int, m: int, d: int):
    from datetime import datetime

    return datetime(y, m, d, 0, 0, 0)


@pytest.mark.asyncio
async def test_create_theme_rejects_duplicate_name():
    existing = ThemeInDB(
        id=uuid4(),
        name="Work",
        color="#FFFFFF",
        created_at=_dt(2026, 1, 1),
        updated_at=_dt(2026, 1, 1),
    )
    repo = DummyThemeRepo()
    repo.get_by_name_result = existing
    service = ThemeService(theme_repo=repo)

    with pytest.raises(ValueError, match="name already exists"):
        await service.create_theme(ThemeCreate(name="Work"))


@pytest.mark.asyncio
async def test_create_theme_rejects_all_themes_title():
    repo = DummyThemeRepo()
    service = ThemeService(theme_repo=repo)

    with pytest.raises(ValueError, match="Invalid theme title"):
        await service.create_theme(ThemeCreate(name="Все темы"))


@pytest.mark.asyncio
async def test_create_theme_validates_color_uniqueness_when_provided():
    existing = ThemeInDB(
        id=uuid4(),
        name="X",
        color="#AA00AA",
        created_at=_dt(2026, 1, 1),
        updated_at=_dt(2026, 1, 1),
    )
    repo = DummyThemeRepo()
    repo.get_by_color_result = existing
    service = ThemeService(theme_repo=repo)

    with pytest.raises(ValueError, match="color already exists"):
        await service.create_theme(ThemeCreate(name="New", color="#AA00AA"))


@pytest.mark.asyncio
async def test_generate_color_falls_back_to_random_on_collision(monkeypatch):
    repo = DummyThemeRepo()
    service = ThemeService(theme_repo=repo)

    base = string_to_hex("Work")
    # First call collides, second is free
    # First call to get_by_color should return an existing theme, all subsequent calls
    # should report that the color is free so that generate_color stops quickly.
    calls = {"count": 0}

    async def fake_get_by_color(color: str) -> ThemeInDB | None:
        if calls["count"] == 0:
            calls["count"] += 1
            return ThemeInDB(
                id=uuid4(),
                name="Existing",
                color=base,
                created_at=_dt(2026, 1, 1),
                updated_at=_dt(2026, 1, 1),
            )
        return None

    repo.get_by_color = fake_get_by_color  # type: ignore[assignment]

    monkeypatch.setattr("src.services.themes.generate_random_hex", lambda: "#123456")

    color = await service.generate_color("Work")
    assert color == "#123456"


@pytest.mark.asyncio
async def test_update_theme_returns_old_when_no_changes():
    old = ThemeInDB(
        id=uuid4(),
        name="Hobby",
        color="#FF00FF",
        created_at=_dt(2026, 1, 1),
        updated_at=_dt(2026, 1, 1),
    )
    repo = DummyThemeRepo()
    repo.get_by_name_result = old
    service = ThemeService(theme_repo=repo)

    res = await service.update_theme(old, ThemeUpdate())
    assert res == old
    assert repo.update_called is False


@pytest.mark.asyncio
async def test_update_theme_rejects_name_conflict():
    old = ThemeInDB(
        id=uuid4(),
        name="Hobby",
        color="#FF00FF",
        created_at=_dt(2026, 1, 1),
        updated_at=_dt(2026, 1, 1),
    )
    taken = ThemeInDB(
        id=uuid4(),
        name="Work",
        color="#00FF00",
        created_at=_dt(2026, 1, 1),
        updated_at=_dt(2026, 1, 1),
    )
    repo = DummyThemeRepo()
    # First call: current theme; second call inside update_theme: conflicting one
    repo.get_by_name_result = taken
    service = ThemeService(theme_repo=repo)

    with pytest.raises(ValueError, match="name already exists"):
        await service.update_theme(old, ThemeUpdate(name="Work"))
