from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import asc, delete as sa_delete, desc, func, select, update
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import SQLColumnExpression

from src.database.models import Habit, HabitCompletion
from src.schemas.habits import (
    HabitCreate,
    HabitInDB,
    HabitOrder,
    HabitScheduleFilter,
    HabitSort,
    HabitStatus,
    HabitUpdate,
)

from .owned_base import OwnedRepository


class HabitRepository(
    OwnedRepository[HabitCreate, HabitInDB, HabitUpdate, Habit, UUID]
):
    _model = Habit
    _create_schema = HabitCreate
    _read_schema = HabitInDB
    _update_schema = HabitUpdate

    async def list_habits(
        self,
        *,
        skip: int,
        limit: int,
        theme_id: UUID | None,
        today: date,
        status: HabitStatus,
        schedule_type: HabitScheduleFilter,
        sort: HabitSort,
        order: HabitOrder,
    ) -> tuple[list[HabitInDB], int]:
        stmt = select(Habit).where(self._owner_filter(Habit.owner_id))

        if theme_id:
            stmt = stmt.where(Habit.theme_id == theme_id)

        completed_today_exists = (
            select(HabitCompletion.id)
            .where(HabitCompletion.habit_id == Habit.id)
            .where(HabitCompletion.completed_on == today)
            .exists()
        )

        if status == "todays":
            stmt = stmt.where(Habit.is_archived.is_(False))
            stmt = stmt.where(~completed_today_exists)
        elif status == "active":
            stmt = stmt.where(Habit.is_archived.is_(False))
        elif status == "completed":
            stmt = stmt.where(Habit.is_archived.is_(False))
            stmt = stmt.where(completed_today_exists)
        elif status == "archived":
            stmt = stmt.where(Habit.is_archived.is_(True))

        if schedule_type != "all":
            stmt = stmt.where(Habit.schedule_type == schedule_type)

        count_stmt = select(func.count()).select_from(
            stmt.with_only_columns(Habit.id).order_by(None).subquery()
        )
        total = await self._session.scalar(count_stmt)

        order_fn = desc if order == "desc" else asc
        sort_col: SQLColumnExpression[Any]

        if sort == "updated_at":
            sort_col = Habit.updated_at
        elif sort == "name":
            sort_col = Habit.name
        elif sort == "streak":
            streak_count = func.count(HabitCompletion.id)
            stmt = stmt.outerjoin(HabitCompletion, HabitCompletion.habit_id == Habit.id)
            stmt = stmt.group_by(Habit.id)
            sort_col = streak_count
        else:
            sort_col = Habit.created_at

        stmt = stmt.order_by(order_fn(sort_col), order_fn(Habit.created_at))
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        records = result.scalars().unique().all()

        return ([self._convert_model_to_read(rec) for rec in records], int(total or 0))

    async def archive_expired_habits(self, today: date) -> int:
        ids_stmt = (
            select(Habit.id)
            .where(self._owner_filter(Habit.owner_id))
            .where(Habit.is_archived.is_(False))
            .where(Habit.ends_on.is_not(None))
            .where(Habit.ends_on < today)
        )
        ids_result = await self._session.execute(ids_stmt)
        habit_ids = ids_result.scalars().all()
        if not habit_ids:
            return 0

        stmt = (
            update(Habit)
            .where(Habit.id.in_(habit_ids))
            .where(self._owner_filter(Habit.owner_id))
            .values(is_archived=True)
        )
        await self._session.execute(stmt)
        await self._session.flush()
        return len(habit_ids)

    async def list_completion_dates(self, habit_id: UUID) -> set[date]:
        stmt = (
            select(HabitCompletion.completed_on)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .where(HabitCompletion.habit_id == habit_id)
            .where(self._owner_filter(Habit.owner_id))
        )
        result = await self._session.execute(stmt)
        dates = result.scalars().all()
        return set(dates)

    async def add_completion(self, habit_id: UUID, completed_on: date) -> bool:
        habit_result = await self._session.execute(
            self._construct_owned_habit_stmt(habit_id)
        )
        if habit_result.scalar_one_or_none() is None:
            return False

        exists_stmt = self._construct_completion_stmt(
            habit_id=habit_id, completed_on=completed_on
        )
        exists_result = await self._session.execute(exists_stmt)
        existing = exists_result.scalars().first()
        if existing:
            return False

        completion = HabitCompletion(habit_id=habit_id, completed_on=completed_on)
        self._session.add(completion)
        await self._session.flush()
        return True

    async def remove_completion(self, habit_id: UUID, completed_on: date) -> bool:
        exists_stmt = (
            select(HabitCompletion.id)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .where(HabitCompletion.habit_id == habit_id)
            .where(HabitCompletion.completed_on == completed_on)
            .where(self._owner_filter(Habit.owner_id))
        )
        exists_result = await self._session.execute(exists_stmt)
        if exists_result.scalar_one_or_none() is None:
            return False

        stmt = (
            sa_delete(HabitCompletion)
            .where(HabitCompletion.habit_id == habit_id)
            .where(HabitCompletion.completed_on == completed_on)
            .where(
                HabitCompletion.habit_id.in_(self._construct_owned_habit_stmt(habit_id))
            )
        )
        await self._session.execute(stmt)
        await self._session.flush()
        return True

    def _construct_owned_habit_stmt(self, habit_id: UUID) -> Select[tuple[UUID]]:
        return select(Habit.id).where(
            Habit.id == habit_id,
            self._owner_filter(Habit.owner_id),
        )

    def _construct_completion_stmt(
        self, habit_id: UUID, completed_on: date
    ) -> Select[tuple[HabitCompletion]]:
        return (
            select(HabitCompletion)
            .join(Habit, Habit.id == HabitCompletion.habit_id)
            .where(HabitCompletion.habit_id == habit_id)
            .where(HabitCompletion.completed_on == completed_on)
            .where(self._owner_filter(Habit.owner_id))
        )
