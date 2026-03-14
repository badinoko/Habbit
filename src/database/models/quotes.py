from enum import Enum as PyEnum

from sqlalchemy import (
    UUID,
    Column,
    Enum,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class TaskStatus(PyEnum):
    pending = "pending"
    ready = "ready"
    failed = "failed"


class QuoteBatch(BaseModel):
    __tablename__ = "quote_batches"

    source = Column(String(128), nullable=False)
    status = Column[TaskStatus](
        Enum(TaskStatus, name="task_status"),
        nullable=False,
        index=True,
    )

    quotes = relationship("Quote", back_populates="quote_batch")


class Quote(BaseModel):
    __tablename__ = "quotes"

    batch_id = Column(
        UUID,
        ForeignKey("quote_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text = Column(String(256), nullable=False)
    author = Column(String(128))
    lang = Column(String(64))

    quote_batch = relationship("QuoteBatch", back_populates="quotes")
