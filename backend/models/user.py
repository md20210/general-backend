"""User model with fastapi-users integration."""
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model with UUID primary key."""

    __tablename__ = "users"

    # Additional fields beyond fastapi-users defaults
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="user", cascade="all, delete-orphan")
    # NOTE: LifeChronicle relationship not needed here - we query entries directly via user_id

    def __repr__(self):
        return f"<User {self.email} (admin={self.is_admin})>"
