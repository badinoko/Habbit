import pytest
from httpx import AsyncClient

from tests.api_unit.assertions import assert_html_response

pytestmark = pytest.mark.asyncio


async def test_get_stats_page_smoke(client: AsyncClient) -> None:
    response = await client.get("/stats")

    assert_html_response(response, status_code=200)
    assert "Statistics v2" in response.text
    assert "/stats?range=30d" in response.text
    assert "Создано за 30 дней" in response.text
    assert "Daily trend" in response.text
    assert "Топ тем по числу привычек" in response.text
