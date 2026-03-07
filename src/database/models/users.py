from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String(254), nullable=False)
    password_hash = Column(String(256), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default=true())

    oauth_accounts = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    __table_args__ = (Index("uq_users_email_lower", func.lower(email), unique=True),)

    themes = relationship("Theme", back_populates="owner", passive_deletes=True)
    tasks = relationship("Task", back_populates="owner", passive_deletes=True)
    habits = relationship("Habit", back_populates="owner", passive_deletes=True)


class OAuthAccount(BaseModel):
    __tablename__ = "oauth_accounts"

    user_id = Column(UUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(128), nullable=False)
    provider_user_id = Column(String(256), nullable=False)
    provider_email = Column(String(254), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_oauth_provider_user",
        ),
        Index(
            "idx_oauth_user_provider",
            "user_id",
            "provider",
        ),
    )

    user = relationship("User", back_populates="oauth_accounts")
