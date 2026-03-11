from sqlalchemy import CheckConstraint, Column, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import OwnedModel


class Theme(OwnedModel):
    __tablename__ = "themes"

    name = Column(String(24), nullable=False)
    color = Column(String(7), nullable=False)

    __table_args__ = (
        CheckConstraint("LENGTH(color) >= 7", name="min_color_length"),
        UniqueConstraint("owner_id", "name", name="uq_themes_owner_id_name"),
    )

    tasks = relationship("Task", back_populates="theme")
    habits = relationship("Habit", back_populates="theme")
    owner = relationship("User", back_populates="themes")
