from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from fastapi import Request
from httpx import ASGITransport, AsyncClient

from src.dependencies import get_habit_service, get_task_service
from src.main import app
from src.schemas.statistics import (
    HabitStatisticsPage,
    StatisticsPageData,
    TaskStatisticsPage,
)
from src.utils import ensure_csrf_token, get_template_context
from tests.api_unit.assertions import assert_html_response

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def stats_client() -> AsyncGenerator[tuple[AsyncClient, dict[str, object]], None]:
    captured: dict[str, object] = {}

    class FakeTaskService:
        async def get_task_page_statistics(self) -> TaskStatisticsPage:
            return TaskStatisticsPage(
                total=3,
                active=2,
                completed=1,
                completion_rate=33,
                by_priority={"low": 1, "medium": 1, "high": 1},
                by_theme={"Без темы": 2, "Работа": 1},
                created_in_7d=2,
                created_in_30d=3,
                completed_in_7d=1,
                completed_in_30d=1,
                avg_completion_time_hours=12.0,
            )

    class FakeHabitService:
        async def get_habit_page_statistics(
            self, selected_range: str = "7d"
        ) -> HabitStatisticsPage:
            return HabitStatisticsPage(
                total=4,
                active=3,
                archived=1,
                due_today=2,
                completed_today=1,
                success_rate_today=50,
                success_rate_7d=67,
                success_rate_30d=72,
                schedule_type_distribution={"Ежедневно": 2, "Дни недели": 1},
                completions_by_day=[
                    {"label": "01.01", "value": 1},
                    {"label": "02.01", "value": 0},
                ],
                top_streaks=[{"label": "Morning walk", "value": 5}],
                top_themes=[{"label": "Здоровье", "value": 2}],
            )

    async def fake_template_context(request: Request) -> dict[str, object]:
        context = {
            "request": request,
            "themes": [],
            "stats": {"active_tasks": 0, "total_habits": 0, "success_rate": 0},
            "current_user": None,
            "current_user_display_name": None,
            "csrf_token": ensure_csrf_token(request),
        }
        captured["context"] = context
        return context

    app.dependency_overrides[get_template_context] = fake_template_context
    app.dependency_overrides[get_task_service] = lambda: FakeTaskService()
    app.dependency_overrides[get_habit_service] = lambda: FakeHabitService()
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, captured
    finally:
        app.dependency_overrides.clear()


async def test_get_stats_returns_html_and_sets_current_page(
    stats_client: tuple[AsyncClient, dict[str, object]],
) -> None:
    client, captured = stats_client

    response = await client.get("/stats")

    assert_html_response(response, status_code=200)
    assert "Statistics v2" in response.text
    assert "Создано за 7 дней" in response.text
    assert "Создано за 30 дней" not in response.text
    assert "Success rate 30d" in response.text
    assert "Самая загруженная тема" in response.text
    context = captured["context"]
    assert isinstance(context, dict)
    assert context["current_page"] == "stats"
    assert isinstance(context["page_data"], StatisticsPageData)
    assert context["page_data"].range == "7d"
    assert context["page_data"].tasks.total == 3
    assert context["page_data"].tasks.completed == 1
    assert context["page_data"].habits.total == 4
    assert context["page_data"].habits.success_rate_7d == 67
    assert context["page_data"].kpis[0].value == 2
    assert context["page_data"].kpis[1].value == 1
    assert context["page_data"].kpis[2].value == 4
    assert context["page_data"].kpis[6].value == "50%"


async def test_get_stats_supports_30d_range(
    stats_client: tuple[AsyncClient, dict[str, object]],
) -> None:
    client, captured = stats_client

    response = await client.get("/stats?range=30d")

    assert_html_response(response, status_code=200)
    assert "Создано за 30 дней" in response.text
    assert "Создано за 7 дней" not in response.text
    assert "Завершено за 30 дней" in response.text
    assert "Завершено за 7 дней" not in response.text
    context = captured["context"]
    assert isinstance(context, dict)
    assert isinstance(context["page_data"], StatisticsPageData)
    assert context["page_data"].range == "30d"


async def test_get_stats_rejects_invalid_range(
    stats_client: tuple[AsyncClient, dict[str, object]],
) -> None:
    client, _ = stats_client

    response = await client.get("/stats?range=365d")

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "range"]
