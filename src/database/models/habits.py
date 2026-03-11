from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import BaseModel, OwnedModel


class Habit(OwnedModel):
    __tablename__ = "habits"

    name = Column(String(46), nullable=False)
    description = Column(String(200), nullable=True)
    theme_id = Column(UUID, ForeignKey("themes.id", ondelete="SET NULL"), nullable=True)
    schedule_type = Column(String(20), nullable=False, default="daily", index=True)
    schedule_config = Column(JSON, nullable=False, default=dict)
    starts_on = Column(Date, nullable=True)
    ends_on = Column(Date, nullable=True, index=True)
    is_archived = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        CheckConstraint(
            "schedule_type IN "
            "('daily','weekly_days','monthly_day','yearly_date','interval_cycle')",
            name="habit_schedule_type_check",
        ),
    )

    theme = relationship("Theme", back_populates="habits")
    completions = relationship(
        "HabitCompletion",
        back_populates="habit",
        cascade="all, delete-orphan",
    )
    owner = relationship("User", back_populates="habits")


class HabitCompletion(BaseModel):
    __tablename__ = "habit_completions"

    habit_id = Column(UUID, ForeignKey("habits.id", ondelete="CASCADE"), nullable=False)
    completed_on = Column(Date, nullable=False)
    note = Column(String(200), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "habit_id",
            "completed_on",
            name="uq_habit_completion_habit_date",
        ),
    )

    habit = relationship("Habit", back_populates="completions")
