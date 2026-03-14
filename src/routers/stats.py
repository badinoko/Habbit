from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import HTMLResponse

from src.dependencies import get_habit_service, get_task_service
from src.schemas.statistics import (
    HabitStatisticsPage,
    StatisticsPageData,
    StatsInsight,
    StatsKpi,
    StatsRange,
    TaskStatisticsPage,
    ThemeStatisticsPage,
)
from src.services.habits import HabitService
from src.services.tasks import TaskService
from src.utils import get_template_context, templates

router = APIRouter(tags=["Statistics"])


def _build_stats_page_data(
    selected_range: StatsRange,
    task_stats: TaskStatisticsPage,
    habit_stats: HabitStatisticsPage,
) -> StatisticsPageData:
    return StatisticsPageData(
        range=selected_range,
        kpis=[
            StatsKpi(
                key="active_tasks",
                label="Активные задачи",
                value=task_stats.active,
                hint="Обновляется по реальным задачам пользователя.",
            ),
            StatsKpi(
                key="completed_tasks",
                label="Выполненные задачи",
                value=task_stats.completed,
                hint="Обновляется по реальным задачам пользователя.",
            ),
            StatsKpi(
                key="total_habits",
                label="Всего привычек",
                value=habit_stats.total,
                hint="Считает все привычки пользователя, включая архивные.",
            ),
            StatsKpi(
                key="active_habits",
                label="Активные привычки",
                value=habit_stats.active,
                hint="Показывает только текущие неархивные привычки.",
            ),
            StatsKpi(
                key="due_today",
                label="Привычки на сегодня",
                value=habit_stats.due_today,
                hint="Учитывает только привычки, которые еще актуальны сегодня.",
            ),
            StatsKpi(
                key="completed_today",
                label="Выполнено сегодня",
                value=habit_stats.completed_today,
                hint="Обновляется по истории выполнений привычек.",
            ),
            StatsKpi(
                key="success_rate",
                label="Success rate",
                value=f"{habit_stats.success_rate_today}%",
                hint="Текущий успех по обязательным привычкам на сегодня.",
            ),
        ],
        tasks=task_stats,
        habits=habit_stats,
        themes=ThemeStatisticsPage(),
        insights=[
            StatsInsight(
                title="Задачи и привычки подключены",
                description="Страница `/stats` уже показывает реальные агрегаты по задачам и привычкам пользователя.",
                severity="info",
            )
        ],
    )


@router.get(
    "/stats",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    summary="Returns statistics page",
)
async def stats_page(
    request: Request,
    context: dict[str, Any] = Depends(get_template_context),
    task_service: TaskService = Depends(get_task_service),
    habit_service: HabitService = Depends(get_habit_service),
    selected_range: Annotated[StatsRange, Query(alias="range")] = "7d",
):
    task_stats = await task_service.get_task_page_statistics()
    habit_stats = await habit_service.get_habit_page_statistics(selected_range)
    context.update(
        {
            "current_page": "stats",
            "page_data": _build_stats_page_data(
                selected_range, task_stats, habit_stats
            ),
        }
    )
    return templates.TemplateResponse(request, "stats/stats_page.html", context)
