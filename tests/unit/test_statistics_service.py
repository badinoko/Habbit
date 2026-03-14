from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from src.schemas.statistics import (
    HabitStatisticsPage,
    StatisticsPageData,
    StatsBreakdownItem,
    TaskStatisticsPage,
)
from src.schemas.tasks import TaskInDB
from src.schemas.themes import ThemeResponse
from src.services.statistics import StatisticsService


def _dt(y: int, m: int, d: int, h: int = 0) -> datetime:
    return datetime(y, m, d, h, 0, 0, tzinfo=UTC)


def _mk_task(
    *,
    theme_id: UUID | None = None,
    completed_at: datetime | None = None,
    created_at: datetime | None = None,
) -> TaskInDB:
    created = created_at or _dt(2026, 3, 1)
    return TaskInDB(
        id=uuid4(),
        name="task",
        description=None,
        theme_id=theme_id,
        priority_id=UUID("00000000-0000-0000-0000-000000000001"),
        completed_at=completed_at,
        created_at=created,
        updated_at=created,
    )


class FakeTaskService:
    def __init__(
        self,
        *,
        task_stats: TaskStatisticsPage,
        tasks: list[TaskInDB],
    ) -> None:
        self.task_stats = task_stats
        self.tasks = tasks
        self.page_statistics_now: datetime | None = None
        self.page_statistics_tasks: list[TaskInDB] | None = None
        self.page_statistics_theme_names: dict[UUID, str] | None = None
        self.get_tasks_for_statistics_calls = 0

    async def get_task_page_statistics(
        self,
        now: datetime | None = None,
        tasks: list[TaskInDB] | None = None,
        theme_names: dict[UUID, str] | None = None,
    ) -> TaskStatisticsPage:
        self.page_statistics_now = now
        self.page_statistics_tasks = tasks
        self.page_statistics_theme_names = theme_names
        return self.task_stats

    async def get_tasks_for_statistics(self) -> list[TaskInDB]:
        self.get_tasks_for_statistics_calls += 1
        return list(self.tasks)


class FakeHabitService:
    def __init__(self, habit_stats: HabitStatisticsPage) -> None:
        self.habit_stats = habit_stats
        self.selected_range: str | None = None
        self.reference_time: datetime | None = None

    async def get_habit_page_statistics(
        self,
        selected_range: str = "7d",
        *,
        reference_time: datetime | None = None,
    ) -> HabitStatisticsPage:
        self.selected_range = selected_range
        self.reference_time = reference_time
        return self.habit_stats


class FakeThemeService:
    def __init__(self, themes: list[ThemeResponse]) -> None:
        self.themes = themes
        self.last_limit: int | None = 100

    async def list_themes(
        self, skip: int = 0, limit: int | None = 100
    ) -> list[ThemeResponse]:
        assert skip == 0
        self.last_limit = limit
        return list(self.themes)


@pytest.mark.asyncio
async def test_statistics_service_aggregates_sections_and_builds_insights() -> None:
    work_theme_id = uuid4()
    health_theme = ThemeResponse(id=work_theme_id, name="Работа", color="#112233")
    task_stats = TaskStatisticsPage(
        total=4,
        active=3,
        completed=1,
        completion_rate=25,
        by_priority={"low": 2, "medium": 1, "high": 1},
        by_theme={"Работа": 3, "Без темы": 1},
        created_in_7d=4,
        created_in_30d=4,
        completed_in_7d=1,
        completed_in_30d=1,
        avg_completion_time_hours=10.0,
    )
    tasks = [
        _mk_task(theme_id=work_theme_id),
        _mk_task(theme_id=work_theme_id),
        _mk_task(theme_id=work_theme_id, completed_at=_dt(2026, 3, 10, 9)),
        _mk_task(theme_id=None),
    ]
    habit_stats = HabitStatisticsPage(
        total=5,
        active=4,
        archived=1,
        due_today=3,
        completed_today=1,
        success_rate_today=33,
        success_rate_7d=57,
        success_rate_30d=61,
        top_streaks=[StatsBreakdownItem(label="Зарядка", value=8)],
        top_themes=[StatsBreakdownItem(label="Здоровье", value=3)],
    )

    service = StatisticsService(
        task_service=FakeTaskService(task_stats=task_stats, tasks=tasks),
        habit_service=FakeHabitService(habit_stats),
        theme_service=FakeThemeService([health_theme]),
    )

    page_data = await service.get_statistics_page_data("30d")

    assert isinstance(page_data, StatisticsPageData)
    assert page_data.range == "30d"
    assert page_data.tasks == task_stats
    assert page_data.habits == habit_stats
    assert page_data.kpis[0].value == 3
    assert page_data.kpis[2].value == 5
    assert page_data.kpis[6].value == "33%"
    assert page_data.themes.top_task_themes == [
        StatsBreakdownItem(label="Работа", value=3),
        StatsBreakdownItem(label="Без темы", value=1),
    ]
    assert page_data.themes.top_habit_themes == [
        StatsBreakdownItem(label="Здоровье", value=3)
    ]
    assert page_data.themes.busiest_theme == StatsBreakdownItem(
        label="Работа", value=2
    )
    assert [insight.title for insight in page_data.insights] == [
        "Осталось привычек на сегодня",
        "Лучшая серия",
        "Самая загруженная тема",
    ]
    assert page_data.insights[0].description == "2 из 3"
    assert page_data.insights[1].description == "Зарядка: 8"
    assert page_data.insights[2].description == "Работа: 2 активных задач"
    assert service.task_service.get_tasks_for_statistics_calls == 1
    assert service.task_service.page_statistics_tasks == tasks
    assert service.task_service.page_statistics_theme_names == {
        work_theme_id: "Работа"
    }
    assert service.habit_service.reference_time == service.task_service.page_statistics_now


@pytest.mark.asyncio
async def test_statistics_service_handles_empty_state_without_failing() -> None:
    service = StatisticsService(
        task_service=FakeTaskService(task_stats=TaskStatisticsPage(), tasks=[]),
        habit_service=FakeHabitService(HabitStatisticsPage()),
        theme_service=FakeThemeService([]),
    )

    page_data = await service.get_statistics_page_data("7d")

    assert page_data.range == "7d"
    assert page_data.tasks == TaskStatisticsPage()
    assert page_data.habits == HabitStatisticsPage()
    assert page_data.themes.top_task_themes == []
    assert page_data.themes.top_habit_themes == []
    assert page_data.themes.busiest_theme is None
    assert len(page_data.insights) == 1
    assert page_data.insights[0].title == "Осталось привычек на сегодня"
    assert page_data.insights[0].description == "0 из 0"
    assert page_data.insights[0].severity == "success"


@pytest.mark.asyncio
async def test_statistics_service_skips_blank_or_duplicate_insights() -> None:
    theme_id = uuid4()
    task_stats = TaskStatisticsPage(active=1, by_theme={"Работа": 1})
    tasks = [_mk_task(theme_id=theme_id)]
    habit_stats = HabitStatisticsPage(
        due_today=1,
        completed_today=1,
        top_streaks=[
            StatsBreakdownItem(label="   ", value=5),
            StatsBreakdownItem(label="Фокус", value=4),
        ],
        top_themes=[StatsBreakdownItem(label="Работа", value=1)],
    )

    service = StatisticsService(
        task_service=FakeTaskService(task_stats=task_stats, tasks=tasks),
        habit_service=FakeHabitService(habit_stats),
        theme_service=FakeThemeService(
            [ThemeResponse(id=theme_id, name="Работа", color="#445566")]
        ),
    )

    page_data = await service.get_statistics_page_data()

    titles = [insight.title for insight in page_data.insights]
    assert len(titles) == len(set(titles))
    assert all(insight.description.strip() for insight in page_data.insights)
    assert "Лучшая серия" in titles
    assert any(insight.description == "Фокус: 4" for insight in page_data.insights)
