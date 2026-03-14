import re
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories import HabitRepository, TaskRepository, ThemeRepository
from src.schemas import TaskUpdate, ThemeCreate
from tests.api_unit.assertions import assert_html_response
from tests.integration.test_habits import create_habit_and_return_id
from tests.integration.test_tasks import create_task_and_return_id

pytestmark = pytest.mark.asyncio


async def test_get_stats_page_smoke(client: AsyncClient) -> None:
    response = await client.get("/stats")

    assert_html_response(response, status_code=200)
    assert "Statistics v2" in response.text
    assert "/stats?range=30d" in response.text
    assert 'class="stats-kpi-grid"' in response.text
    assert "Пульс задач" in response.text
    assert "Фокус периода" in response.text
    assert "Создано за 7 дней" in response.text
    assert "Создано за 30 дней" not in response.text
    assert "Daily trend" in response.text
    assert "Топ тем по числу привычек" in response.text
    assert 'class="stats-insight-list"' in response.text


def _assert_task_stat_value(html: str, label: str, value: str) -> None:
    pattern = (
        r'<h2><i class="fas fa-tasks"></i> Задачи</h2>.*?'
        + r"<span>\s*"
        + re.escape(label)
        + r"\s*</span>"
        + r"\s*<strong>\s*"
        + re.escape(value)
        + r"\s*</strong>"
    )
    assert re.search(pattern, html, re.S), f"Expected task stat {label}={value}"


def _assert_habit_stat_value(html: str, label: str, value: str) -> None:
    pattern = (
        r'<h2><i class="fas fa-sync-alt"></i> Привычки</h2>.*?'
        + r"<span>\s*"
        + re.escape(label)
        + r"\s*</span>"
        + r"\s*<strong>\s*"
        + re.escape(value)
        + r"\s*</strong>"
    )
    assert re.search(pattern, html, re.S), f"Expected habit stat {label}={value}"


async def test_stats_page_shows_owner_task_aggregates_only(
    client: AsyncClient,
    session: AsyncSession,
    owner_id: UUID,
    secondary_owner_id: UUID,
) -> None:
    owner_theme = await ThemeRepository(session=session, owner_id=owner_id).add(
        ThemeCreate(name="Статистика Работа", color="#112233")
    )
    foreign_theme = await ThemeRepository(
        session=session, owner_id=secondary_owner_id
    ).add(ThemeCreate(name="Чужая тема", color="#445566"))
    await session.commit()

    await create_task_and_return_id(
        session,
        owner_id=owner_id,
        name="stats-active-task",
    )
    completed_task_id = await create_task_and_return_id(
        session,
        owner_id=owner_id,
        name="stats-completed-task",
        theme_id=owner_theme.id,
    )
    await create_task_and_return_id(
        session,
        owner_id=secondary_owner_id,
        name="foreign-stats-task",
        theme_id=foreign_theme.id,
    )

    await TaskRepository(session=session, owner_id=owner_id).update(
        completed_task_id,
        TaskUpdate(completed_at=datetime.now(UTC)),
    )
    await session.commit()

    response = await client.get("/stats")

    assert_html_response(response, status_code=200)
    _assert_task_stat_value(response.text, "Всего", "2")
    _assert_task_stat_value(response.text, "Активные", "1")
    _assert_task_stat_value(response.text, "Выполненные", "1")
    _assert_task_stat_value(response.text, "Completion rate", "50%")
    _assert_task_stat_value(response.text, "Создано за 7 дней", "2")
    _assert_task_stat_value(response.text, "Завершено за 7 дней", "1")
    assert "Статистика Работа" in response.text
    assert "Без темы" in response.text
    assert "Чужая тема" not in response.text
    assert "foreign-stats-task" not in response.text


async def test_stats_page_switches_task_period_labels_for_30d(
    client: AsyncClient,
) -> None:
    response = await client.get("/stats?range=30d")

    assert_html_response(response, status_code=200)
    assert "Создано за 30 дней" in response.text
    assert "Создано за 7 дней" not in response.text
    assert "Завершено за 30 дней" in response.text
    assert "Завершено за 7 дней" not in response.text


async def test_stats_page_shows_owner_habit_history_only(
    client: AsyncClient,
    session: AsyncSession,
    owner_id: UUID,
    secondary_owner_id: UUID,
) -> None:
    today = datetime.now(UTC).date()
    weekday = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")[today.weekday()]

    owner_theme = await ThemeRepository(session=session, owner_id=owner_id).add(
        ThemeCreate(name="Фокус", color="#223344")
    )
    foreign_theme = await ThemeRepository(
        session=session, owner_id=secondary_owner_id
    ).add(ThemeCreate(name="Чужая привычка", color="#556677"))
    await session.commit()

    owner_daily_habit_id = await create_habit_and_return_id(
        session,
        owner_id=owner_id,
        name="stats-owner-daily-habit",
        theme_id=owner_theme.id,
        starts_on=today - timedelta(days=6),
    )
    owner_weekly_habit_id = await create_habit_and_return_id(
        session,
        owner_id=owner_id,
        name="stats-owner-weekly-habit",
        schedule_type="weekly_days",
        schedule_config={"days": [weekday]},
        starts_on=today - timedelta(days=6),
    )
    owner_archived_habit_id = await create_habit_and_return_id(
        session,
        owner_id=owner_id,
        name="stats-owner-archived-habit",
        theme_id=owner_theme.id,
        starts_on=today - timedelta(days=2),
        ends_on=today - timedelta(days=1),
    )
    foreign_habit_id = await create_habit_and_return_id(
        session,
        owner_id=secondary_owner_id,
        name="stats-foreign-habit",
        theme_id=foreign_theme.id,
        starts_on=today - timedelta(days=6),
    )

    owner_habit_repo = HabitRepository(session=session, owner_id=owner_id)
    await owner_habit_repo.add_completion(owner_daily_habit_id, today - timedelta(days=1))
    await owner_habit_repo.add_completion(owner_daily_habit_id, today)
    await owner_habit_repo.add_completion(owner_weekly_habit_id, today)
    await owner_habit_repo.add_completion(owner_archived_habit_id, today - timedelta(days=1))

    foreign_habit_repo = HabitRepository(session=session, owner_id=secondary_owner_id)
    await foreign_habit_repo.add_completion(foreign_habit_id, today)
    await session.commit()

    response = await client.get("/stats?range=7d")

    assert_html_response(response, status_code=200)
    _assert_habit_stat_value(response.text, "Всего", "3")
    _assert_habit_stat_value(response.text, "Активные", "2")
    _assert_habit_stat_value(response.text, "Архивные", "1")
    _assert_habit_stat_value(response.text, "На сегодня", "2")
    _assert_habit_stat_value(response.text, "Выполнено сегодня", "2")
    _assert_habit_stat_value(response.text, "Success rate сегодня", "100%")
    _assert_habit_stat_value(response.text, "Success rate 7d", "40%")
    _assert_habit_stat_value(response.text, today.strftime("%d.%m"), "2")
    _assert_habit_stat_value(response.text, (today - timedelta(days=1)).strftime("%d.%m"), "2")
    assert "Фокус" in response.text
    assert "Без темы" in response.text
    assert "stats-owner-daily-habit" in response.text
    assert "stats-owner-weekly-habit" in response.text
    assert "Чужая привычка" not in response.text
    assert "stats-foreign-habit" not in response.text
