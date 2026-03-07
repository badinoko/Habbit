from sqlalchemy import UUID, CheckConstraint, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class Theme(BaseModel):
    __tablename__ = "themes"

    name = Column(String(24), nullable=False)
    color = Column(String(7), nullable=False)
    owner_id = Column(
        UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    __table_args__ = (CheckConstraint("LENGTH(color) >= 7", name="min_color_length"),)

    tasks = relationship("Task", back_populates="theme")
    habits = relationship("Habit", back_populates="theme")
    owner = relationship("User", back_populates="themes")
