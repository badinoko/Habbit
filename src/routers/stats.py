from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import HTMLResponse

from src.schemas.statistics import (
    HabitStatisticsPage,
    StatisticsPageData,
    StatsInsight,
    StatsKpi,
    StatsRange,
    TaskStatisticsPage,
    ThemeStatisticsPage,
)
from src.utils import get_template_context, templates

router = APIRouter(tags=["Statistics"])


def _build_placeholder_page_data(selected_range: StatsRange) -> StatisticsPageData:
    return StatisticsPageData(
        range=selected_range,
        kpis=[
            StatsKpi(
                key="active_tasks",
                label="Активные задачи",
                value=0,
                hint="Будет заполнено в следующих PR.",
            ),
            StatsKpi(
                key="completed_tasks",
                label="Выполненные задачи",
                value=0,
                hint="Будет заполнено в следующих PR.",
            ),
            StatsKpi(
                key="total_habits",
                label="Всего привычек",
                value=0,
                hint="Будет заполнено в следующих PR.",
            ),
            StatsKpi(
                key="active_habits",
                label="Активные привычки",
                value=0,
                hint="Будет заполнено в следующих PR.",
            ),
            StatsKpi(
                key="due_today",
                label="Привычки на сегодня",
                value=0,
                hint="Будет заполнено в следующих PR.",
            ),
            StatsKpi(
                key="completed_today",
                label="Выполнено сегодня",
                value=0,
                hint="Будет заполнено в следующих PR.",
            ),
            StatsKpi(
                key="success_rate",
                label="Success rate",
                value="0%",
                hint="Будет заполнено в следующих PR.",
            ),
        ],
        tasks=TaskStatisticsPage(),
        habits=HabitStatisticsPage(),
        themes=ThemeStatisticsPage(),
        insights=[
            StatsInsight(
                title="Страница готова к расширению",
                description="В PR1 зафиксирован контракт и каркас страницы `/stats`.",
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
    selected_range: Annotated[StatsRange, Query(alias="range")] = "7d",
):
    context.update(
        {
            "current_page": "stats",
            "page_data": _build_placeholder_page_data(selected_range),
        }
    )
    return templates.TemplateResponse(request, "stats/stats_page.html", context)
