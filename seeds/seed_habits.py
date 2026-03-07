# ruff: noqa: E402
import asyncio
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from sqlalchemy import delete, select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import AsyncSessionLocal as async_session_maker
from src.database.models import Habit, HabitCompletion, Theme

SEED_PREFIX = "SEED::"
SEED_THEME_NAME = "SEED::Habits"
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _today_utc() -> date:
    return datetime.now(UTC).date()


def _weekday_code(value: date) -> str:
    return WEEKDAYS[value.weekday()]


def _different_weekday_code(value: date) -> str:
    return WEEKDAYS[(value.weekday() + 1) % 7]


def _monthly_not_due_day(today: date) -> int:
    return 1 if today.day != 1 else 2


def _yearly_not_due_date(today: date) -> date:
    return today + timedelta(days=1)


async def _get_or_create_seed_theme() -> Theme:
    async with async_session_maker() as session:
        existing = (
            await session.execute(select(Theme).where(Theme.name == SEED_THEME_NAME))
        ).scalar_one_or_none()
        if existing:
            return existing

        theme = Theme(name=SEED_THEME_NAME, color="#1F8A70")
        session.add(theme)
        await session.commit()
        await session.refresh(theme)
        return theme


async def _clear_old_seed_habits() -> int:
    async with async_session_maker() as session:
        seed_habits = (
            await session.execute(select(Habit).where(Habit.name.like(f"{SEED_PREFIX}%")))
        ).scalars().all()
        if not seed_habits:
            return 0

        seed_ids = [habit.id for habit in seed_habits]
        await session.execute(
            delete(HabitCompletion).where(HabitCompletion.habit_id.in_(seed_ids))
        )
        await session.execute(delete(Habit).where(Habit.id.in_(seed_ids)))
        await session.commit()
        return len(seed_ids)


async def seed() -> None:
    today = _today_utc()
    seed_theme = await _get_or_create_seed_theme()
    deleted = await _clear_old_seed_habits()

    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    four_days_ago = today - timedelta(days=4)
    three_days_ago = today - timedelta(days=3)
    two_days_ago = today - timedelta(days=2)

    monthly_not_due_day = _monthly_not_due_day(today)
    yearly_not_due = _yearly_not_due_date(today)

    habits = [
        Habit(
            name=f"{SEED_PREFIX}daily_due",
            theme_id=seed_theme.id,
            schedule_type="daily",
            schedule_config={},
            starts_on=today - timedelta(days=10),
        ),
        Habit(
            name=f"{SEED_PREFIX}daily_completed_today",
            theme_id=seed_theme.id,
            schedule_type="daily",
            schedule_config={},
            starts_on=today - timedelta(days=10),
        ),
        Habit(
            name=f"{SEED_PREFIX}daily_starts_tomorrow",
            theme_id=seed_theme.id,
            schedule_type="daily",
            schedule_config={},
            starts_on=tomorrow,
        ),
        Habit(
            name=f"{SEED_PREFIX}daily_ended_yesterday",
            theme_id=seed_theme.id,
            schedule_type="daily",
            schedule_config={},
            starts_on=today - timedelta(days=20),
            ends_on=yesterday,
        ),
        Habit(
            name=f"{SEED_PREFIX}weekly_due",
            theme_id=seed_theme.id,
            schedule_type="weekly_days",
            schedule_config={"days": [_weekday_code(today)]},
            starts_on=today - timedelta(days=20),
        ),
        Habit(
            name=f"{SEED_PREFIX}weekly_not_due",
            theme_id=seed_theme.id,
            schedule_type="weekly_days",
            schedule_config={"days": [_different_weekday_code(today)]},
            starts_on=today - timedelta(days=20),
        ),
        Habit(
            name=f"{SEED_PREFIX}monthly_due",
            theme_id=seed_theme.id,
            schedule_type="monthly_day",
            schedule_config={"day": today.day},
            starts_on=today - timedelta(days=60),
        ),
        Habit(
            name=f"{SEED_PREFIX}monthly_not_due",
            theme_id=seed_theme.id,
            schedule_type="monthly_day",
            schedule_config={"day": monthly_not_due_day},
            starts_on=today - timedelta(days=60),
        ),
        Habit(
            name=f"{SEED_PREFIX}yearly_due",
            theme_id=seed_theme.id,
            schedule_type="yearly_date",
            schedule_config={"month": today.month, "day": today.day},
            starts_on=today - timedelta(days=370),
        ),
        Habit(
            name=f"{SEED_PREFIX}yearly_not_due",
            theme_id=seed_theme.id,
            schedule_type="yearly_date",
            schedule_config={"month": yearly_not_due.month, "day": yearly_not_due.day},
            starts_on=today - timedelta(days=370),
        ),
        Habit(
            name=f"{SEED_PREFIX}interval_due_after_break",
            theme_id=seed_theme.id,
            schedule_type="interval_cycle",
            schedule_config={"active_days": 2, "break_days": 2},
            starts_on=today - timedelta(days=20),
        ),
        Habit(
            name=f"{SEED_PREFIX}interval_not_due_break",
            theme_id=seed_theme.id,
            schedule_type="interval_cycle",
            schedule_config={"active_days": 2, "break_days": 2},
            starts_on=today - timedelta(days=20),
        ),
        Habit(
            name=f"{SEED_PREFIX}interval_due_partial_run",
            theme_id=seed_theme.id,
            schedule_type="interval_cycle",
            schedule_config={"active_days": 2, "break_days": 2},
            starts_on=today - timedelta(days=20),
        ),
    ]

    completion_by_name = {
        f"{SEED_PREFIX}daily_completed_today": [today],
        f"{SEED_PREFIX}interval_due_after_break": [four_days_ago, three_days_ago],
        f"{SEED_PREFIX}interval_not_due_break": [two_days_ago, yesterday],
        f"{SEED_PREFIX}interval_due_partial_run": [yesterday],
    }

    async with async_session_maker() as session:
        session.add_all(habits)
        await session.flush()

        completions: list[HabitCompletion] = []
        for habit in habits:
            completions.extend(
                HabitCompletion(habit_id=habit.id, completed_on=completed_on)
                for completed_on in completion_by_name.get(habit.name, [])
            )

        if completions:
            session.add_all(completions)

        await session.commit()

    print(f"Deleted old seed habits: {deleted}")
    print(f"Inserted habits: {len(habits)}")
    print(
        "Expected due-today on home page: "
        f"{SEED_PREFIX}daily_due, "
        f"{SEED_PREFIX}weekly_due, "
        f"{SEED_PREFIX}monthly_due, "
        f"{SEED_PREFIX}yearly_due, "
        f"{SEED_PREFIX}interval_due_after_break, "
        f"{SEED_PREFIX}interval_due_partial_run"
    )


if __name__ == "__main__":
    asyncio.run(seed())
