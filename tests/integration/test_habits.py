from datetime import UTC, datetime, timedelta
import re
from uuid import UUID

import pytest

from src.repositories import HabitRepository, ThemeRepository
from src.schemas.habits import HabitCreateAPI
from src.services.habits import HabitService

WEEKDAY_BY_INDEX = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


async def mark_habit_as_completed(client, habit_id: UUID):
    return await client.patch(f"/habits/{habit_id}/complete")


@pytest.mark.asyncio
async def test_habits_list_status_filter_todays_active_and_completed(client, session):
    todays_id = await create_habit_and_return_id(session, name="habit-status-todays")
    completed_id = await create_habit_and_return_id(
        session, name="habit-status-completed"
    )

    complete_response = await mark_habit_as_completed(client, completed_id)
    assert complete_response.status_code == 200

    todays_response = await client.get("/habits/?status=todays")
    assert todays_response.status_code == 200
    assert "habit-status-todays" in todays_response.text
    assert "habit-status-completed" not in todays_response.text

    active_response = await client.get("/habits/?status=active")
    assert active_response.status_code == 200
    assert "habit-status-todays" in active_response.text
    assert "habit-status-completed" in active_response.text

    completed_response = await client.get("/habits/?status=completed")
    assert completed_response.status_code == 200
    assert "habit-status-todays" not in completed_response.text
    assert "habit-status-completed" in completed_response.text

    completed_habit = await HabitRepository(session=session).get_by_id(completed_id)
    assert completed_habit is not None
    assert completed_habit.is_archived is False

    todays_habit = await HabitRepository(session=session).get_by_id(todays_id)
    assert todays_habit is not None
    assert todays_habit.is_archived is False


@pytest.mark.asyncio
async def test_habit_moves_to_archive_when_period_is_over(client, session):
    today = datetime.now(UTC).date()
    expired_id = await create_habit_and_return_id(
        session,
        name="habit-expired-archived",
        starts_on=today - timedelta(days=14),
        ends_on=today - timedelta(days=1),
    )

    active_response = await client.get("/habits/?status=active")
    assert active_response.status_code == 200
    assert "habit-expired-archived" not in active_response.text

    archived_response = await client.get("/habits/?status=archived")
    assert archived_response.status_code == 200
    assert "habit-expired-archived" in archived_response.text

    expired_habit = await HabitRepository(session=session).get_by_id(expired_id)
    assert expired_habit is not None
    assert expired_habit.is_archived is True


@pytest.mark.asyncio
async def test_completed_status_excludes_archived_habits(client, session):
    today = datetime.now(UTC).date()
    archived_id = await create_habit_and_return_id(
        session,
        name="habit-archived-not-completed-filter",
        starts_on=today - timedelta(days=5),
        ends_on=today - timedelta(days=1),
    )

    habit_repo = HabitRepository(session=session)
    await habit_repo.add_completion(archived_id, today)
    await session.commit()

    completed_response = await client.get("/habits/?status=completed")
    assert completed_response.status_code == 200
    assert "habit-archived-not-completed-filter" not in completed_response.text

    archived_response = await client.get("/habits/?status=archived")
    assert archived_response.status_code == 200
    assert "habit-archived-not-completed-filter" in archived_response.text


@pytest.mark.asyncio
async def test_todays_status_filters_habits_by_schedule_for_current_date(client, session):
    today = datetime.now(UTC).date()
    today_weekday = WEEKDAY_BY_INDEX[today.weekday()]
    other_weekday = WEEKDAY_BY_INDEX[(today.weekday() + 1) % 7]
    monthly_not_today = 1 if today.day != 1 else 2
    yearly_month, yearly_day = (1, 1) if (today.month, today.day) != (1, 1) else (1, 2)

    await create_habit_and_return_id(
        session,
        name="habit-daily-due-today",
        schedule_type="daily",
        schedule_config={},
    )
    await create_habit_and_return_id(
        session,
        name="habit-weekly-not-today",
        schedule_type="weekly_days",
        schedule_config={"days": [other_weekday]},
    )
    await create_habit_and_return_id(
        session,
        name="habit-weekly-due-today",
        schedule_type="weekly_days",
        schedule_config={"days": [today_weekday]},
    )
    await create_habit_and_return_id(
        session,
        name="habit-monthly-not-today",
        schedule_type="monthly_day",
        schedule_config={"day": monthly_not_today},
    )
    await create_habit_and_return_id(
        session,
        name="habit-yearly-not-today",
        schedule_type="yearly_date",
        schedule_config={"month": yearly_month, "day": yearly_day},
    )

    response = await client.get("/habits/?status=todays")
    assert response.status_code == 200
    assert "habit-daily-due-today" in response.text
    assert "habit-weekly-due-today" in response.text
    assert "habit-weekly-not-today" not in response.text
    assert "habit-monthly-not-today" not in response.text
    assert "habit-yearly-not-today" not in response.text


@pytest.mark.asyncio
async def test_delete_habit_updates_sidebar_stats_and_success_rate(client, session):
    habit_id = await create_habit_and_return_id(
        session,
        name="habit-delete-stats-updated",
        schedule_type="daily",
        schedule_config={},
    )
    complete_response = await mark_habit_as_completed(client, habit_id)
    assert complete_response.status_code == 200

    before_response = await client.get("/habits/?status=active")
    assert before_response.status_code == 200
    assert "habit-delete-stats-updated" in before_response.text

    before_total = _extract_stat_value(before_response.text, "stat-total-habits")
    before_active = _extract_stat_value(before_response.text, "stat-active-habits")
    before_due_counter = _extract_stat_value(
        before_response.text, "stat-due-habits-today"
    )
    (
        before_due_data,
        before_completed_data,
        before_success_rate,
    ) = _extract_success_rate_payload(before_response.text)

    assert before_due_counter == before_due_data
    assert before_due_data >= 1
    assert before_completed_data >= 1
    assert before_success_rate == round((before_completed_data / before_due_data) * 100)

    delete_response = await client.delete(f"/habits/{habit_id}")
    assert delete_response.status_code == 204

    after_response = await client.get("/habits/?status=active")
    assert after_response.status_code == 200
    assert "habit-delete-stats-updated" not in after_response.text

    after_total = _extract_stat_value(after_response.text, "stat-total-habits")
    after_active = _extract_stat_value(after_response.text, "stat-active-habits")
    after_due_counter = _extract_stat_value(after_response.text, "stat-due-habits-today")
    (
        after_due_data,
        after_completed_data,
        after_success_rate,
    ) = _extract_success_rate_payload(after_response.text)

    assert after_total == before_total - 1
    assert after_active == before_active - 1
    assert after_due_counter == max(0, before_due_counter - 1)
    assert after_due_data == max(0, before_due_data - 1)
    assert after_completed_data == max(0, before_completed_data - 1)

    expected_success_rate = (
        round((after_completed_data / after_due_data) * 100) if after_due_data else 0
    )
    assert after_success_rate == expected_success_rate


def _extract_stat_value(html: str, element_id: str) -> int:
    pattern = rf'id="{element_id}"[^>]*>\s*(\d+)(?:%|)\s*<'
    match = re.search(pattern, html)
    assert match is not None, f"Stat element not found: {element_id}"
    return int(match.group(1))


def _extract_success_rate_payload(html: str) -> tuple[int, int, int]:
    tag_match = re.search(r'<span[^>]*id="stat-success-rate"[^>]*>', html)
    assert tag_match is not None, "Success rate element not found"
    tag = tag_match.group(0)

    due_match = re.search(r'data-due-habits-today="(\d+)"', tag)
    completed_match = re.search(r'data-completed-habits-today="(\d+)"', tag)
    value_match = re.search(r">(\d+)%<", html[tag_match.end() - 1 :])

    assert due_match is not None, "Missing data-due-habits-today"
    assert completed_match is not None, "Missing data-completed-habits-today"
    assert value_match is not None, "Missing success-rate value"

    return int(due_match.group(1)), int(completed_match.group(1)), int(value_match.group(1))


async def create_habit_and_return_id(
    session,
    *,
    name: str,
    schedule_type="daily",
    schedule_config=None,
    starts_on=None,
    ends_on=None,
):
    habit_repo = HabitRepository(session=session)
    theme_repo = ThemeRepository(session=session)
    habit_service = HabitService(habit_repo=habit_repo, theme_repo=theme_repo)

    habit = await habit_service.create_habit(
        HabitCreateAPI(
            name=name,
            schedule_type=schedule_type,
            schedule_config=schedule_config if schedule_config is not None else {},
            starts_on=starts_on,
            ends_on=ends_on,
        )
    )
    await session.commit()
    return habit.id
