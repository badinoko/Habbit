from __future__ import annotations

import pytest
from starlette.datastructures import FormData

from src.routers.habits import _as_positive_int_or_raise, _build_schedule_config_from_form


def test_build_schedule_config_for_daily() -> None:
    form = FormData({})
    assert _build_schedule_config_from_form(form, "daily") == {}


def test_build_schedule_config_for_weekly_days() -> None:
    form = FormData([("weekly_days", "mon"), ("weekly_days", "fri")])
    assert _build_schedule_config_from_form(form, "weekly_days") == {
        "days": ["mon", "fri"]
    }


def test_build_schedule_config_for_monthly_day() -> None:
    form = FormData({"monthly_day": "15"})
    assert _build_schedule_config_from_form(form, "monthly_day") == {"day": 15}


def test_build_schedule_config_for_yearly_date() -> None:
    form = FormData({"yearly_month": "2", "yearly_day": "20"})
    assert _build_schedule_config_from_form(form, "yearly_date") == {
        "month": 2,
        "day": 20,
    }


def test_build_schedule_config_for_interval_cycle() -> None:
    form = FormData({"interval_active_days": "3", "interval_break_days": "2"})
    assert _build_schedule_config_from_form(form, "interval_cycle") == {
        "active_days": 3,
        "break_days": 2,
    }


def test_build_schedule_config_for_unknown_type_returns_empty() -> None:
    form = FormData({})
    assert _build_schedule_config_from_form(form, "unknown") == {}


def test_as_positive_int_or_raise_rejects_non_integer() -> None:
    with pytest.raises(ValueError, match="целым числом больше 0"):
        _as_positive_int_or_raise("abc", "Месяц")


def test_as_positive_int_or_raise_rejects_zero() -> None:
    with pytest.raises(ValueError, match="целым числом больше 0"):
        _as_positive_int_or_raise("0", "День")
