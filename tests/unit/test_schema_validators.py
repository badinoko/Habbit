from __future__ import annotations

import pytest

from src.schemas.tasks import TaskCreateAPI
from src.schemas.themes import ThemeCreate


def test_task_create_api_maps_special_no_theme_uuid_to_none() -> None:
    data = TaskCreateAPI(
        name="task",
        description=None,
        theme_id="00000000-0000-0000-0000-000000000001",
        priority="low",
    )
    assert data.theme_id is None


def test_theme_create_rejects_invalid_hex_color() -> None:
    with pytest.raises(ValueError, match="Некорректный формат цвета"):
        ThemeCreate(name="Hobby", color="#12ZZ56")
