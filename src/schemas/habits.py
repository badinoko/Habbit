from __future__ import annotations

import json
from calendar import monthrange
from collections.abc import Callable
from datetime import date as dt_date
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .base import InDBBase

HabitStatus = Literal["todays", "completed", "active", "archived"]
HabitScheduleType = Literal[
    "daily",
    "weekly_days",
    "monthly_day",
    "yearly_date",
    "interval_cycle",
]
HabitScheduleFilter = Literal[
    "daily",
    "weekly_days",
    "monthly_day",
    "yearly_date",
    "interval_cycle",
    "all",
]
HabitSort = Literal["created_at", "updated_at", "name", "streak"]
HabitOrder = Literal["asc", "desc"]
Weekday = Literal["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

WEEKDAY_ORDER: dict[Weekday, int] = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}

NO_THEME_IDS = {
    "NoTheme",
    "00000000-0000-0000-0000-000000000001",
}


def normalize_schedule_config(
    schedule_type: HabitScheduleType, schedule_config: dict[str, Any]
) -> dict[str, Any]:
    normalizers: dict[HabitScheduleType, Callable[[dict[str, Any]], dict[str, Any]]] = {
        "daily": _normalize_daily,
        "weekly_days": _normalize_weekly_days,
        "monthly_day": _normalize_monthly_day,
        "yearly_date": _normalize_yearly_date,
        "interval_cycle": _normalize_interval_cycle,
    }
    return normalizers[schedule_type](schedule_config)


def _normalize_daily(schedule_config: dict[str, Any]) -> dict[str, Any]:
    if schedule_config != {}:
        raise ValueError("schedule_config must be an empty object for daily")
    return {}


def _normalize_weekly_days(schedule_config: dict[str, Any]) -> dict[str, Any]:
    days = _normalize_days(schedule_config.get("days"))
    if not days:
        raise ValueError("days must be non-empty for weekly_days")
    return {"days": days}


def _normalize_monthly_day(schedule_config: dict[str, Any]) -> dict[str, Any]:
    day = _as_positive_int(schedule_config.get("day"), "day")
    if day > 31:
        raise ValueError("day must be <= 31 for monthly_day")
    return {"day": day}


def _normalize_yearly_date(schedule_config: dict[str, Any]) -> dict[str, Any]:
    month = _as_positive_int(schedule_config.get("month"), "month")
    day = _as_positive_int(schedule_config.get("day"), "day")
    if month > 12:
        raise ValueError("month must be <= 12 for yearly_date")
    max_day = monthrange(2024 if month == 2 else 2025, month)[1]
    if day > max_day:
        raise ValueError("day is invalid for the provided month")
    return {"month": month, "day": day}


def _normalize_interval_cycle(schedule_config: dict[str, Any]) -> dict[str, Any]:
    active_days = _as_positive_int(schedule_config.get("active_days"), "active_days")
    break_days = _as_positive_int(schedule_config.get("break_days"), "break_days")
    return {"active_days": active_days, "break_days": break_days}


def _as_positive_int(value: object, field_name: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer")
    if value < 1:
        raise ValueError(f"{field_name} must be >= 1")
    return value


def _normalize_days(value: object) -> list[Weekday]:
    if not isinstance(value, list):
        raise ValueError("days must be a list")
    result: list[Weekday] = []
    for day in value:
        if day not in WEEKDAY_ORDER:
            raise ValueError("days must contain only mon..sun values")
        if day not in result:
            result.append(day)
    result.sort(key=lambda day: WEEKDAY_ORDER[day])
    return result


def _normalize_theme_id(value: object) -> object:
    if value in NO_THEME_IDS or value == "":
        return None
    return value


def _normalize_schedule_config_value(value: object) -> object:
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return {}
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("schedule_config must be valid JSON object") from exc
        if not isinstance(parsed, dict):
            raise ValueError("schedule_config must be an object")
        return parsed
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("schedule_config must be an object")
    return value


def _normalize_optional_date(value: object) -> object:
    if value == "":
        return None
    return value


class HabitBase(BaseModel):
    name: str = Field(min_length=1, max_length=46)
    description: str | None = Field(None, max_length=200)
    theme_id: UUID | None = Field(None)
    schedule_type: HabitScheduleType
    schedule_config: dict[str, Any] = Field(default_factory=dict)
    starts_on: dt_date | None = None
    ends_on: dt_date | None = None

    @field_validator("theme_id", mode="before")
    @classmethod
    def normalize_theme_id(cls, value: object) -> object:
        return _normalize_theme_id(value)

    @field_validator("schedule_config", mode="before")
    @classmethod
    def normalize_schedule_config_json(cls, value: object) -> object:
        return _normalize_schedule_config_value(value)

    @field_validator("starts_on", "ends_on", mode="before")
    @classmethod
    def normalize_dates(cls, value: object) -> object:
        return _normalize_optional_date(value)

    @model_validator(mode="after")
    def validate_schedule_config(self) -> HabitBase:
        self.schedule_config = normalize_schedule_config(
            self.schedule_type, self.schedule_config
        )
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValueError("ends_on must be greater than or equal to starts_on")
        return self


class HabitCreate(HabitBase):
    pass


class HabitCreateAPI(HabitBase):
    pass


class HabitUpdate(BaseModel):
    name: str | None = Field(None, max_length=46)
    description: str | None = Field(None, max_length=200)
    theme_id: UUID | None = Field(None)
    schedule_type: HabitScheduleType | None = None
    schedule_config: dict[str, Any] | None = None
    starts_on: dt_date | None = None
    ends_on: dt_date | None = None
    is_archived: bool | None = None

    @field_validator("theme_id", mode="before")
    @classmethod
    def normalize_theme_id(cls, value: object) -> object:
        return _normalize_theme_id(value)

    @field_validator("schedule_config", mode="before")
    @classmethod
    def normalize_schedule_config_json(cls, value: object) -> object:
        if value is None:
            return None
        normalized = _normalize_schedule_config_value(value)
        if not isinstance(normalized, dict):
            raise ValueError("schedule_config must be an object")
        return normalized

    @field_validator("starts_on", "ends_on", mode="before")
    @classmethod
    def normalize_dates(cls, value: object) -> object:
        return _normalize_optional_date(value)

    @model_validator(mode="after")
    def validate_schedule_if_fully_provided(self) -> HabitUpdate:
        if self.schedule_type is not None and self.schedule_config is not None:
            self.schedule_config = normalize_schedule_config(
                self.schedule_type, self.schedule_config
            )
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValueError("ends_on must be greater than or equal to starts_on")
        return self


class HabitUpdateAPI(HabitUpdate):
    pass


class HabitInDB(HabitBase, InDBBase):
    is_archived: bool = False
    model_config = ConfigDict(from_attributes=True)


class HabitResponse(HabitInDB):
    theme_name: str | None = None
    theme_color: str | None = None
    current_streak: int = 0
    completed_today: bool = False
    due_today: bool = False
    progress_percent: float = 0.0


class HabitCompletionPayload(BaseModel):
    date: dt_date | None = None


class HabitCompletionResult(BaseModel):
    success: bool
    completed: bool
    date: dt_date
    new_streak: int
    changed: bool


class HabitStatistics(BaseModel):
    total: int
    active: int
    due_today: int
    completed_today: int
    success_rate: int
