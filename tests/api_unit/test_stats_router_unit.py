from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from fastapi import Request
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.schemas.statistics import StatisticsPageData
from src.utils import ensure_csrf_token, get_template_context
from tests.api_unit.assertions import assert_html_response

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def stats_client() -> AsyncGenerator[tuple[AsyncClient, dict[str, object]], None]:
    captured: dict[str, object] = {}

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
    assert "Success rate 30d" in response.text
    assert "Самая загруженная тема" in response.text
    context = captured["context"]
    assert isinstance(context, dict)
    assert context["current_page"] == "stats"
    assert isinstance(context["page_data"], StatisticsPageData)
    assert context["page_data"].range == "7d"


async def test_get_stats_supports_30d_range(
    stats_client: tuple[AsyncClient, dict[str, object]],
) -> None:
    client, captured = stats_client

    response = await client.get("/stats?range=30d")

    assert_html_response(response, status_code=200)
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
