"""User model with fastapi-users integration."""
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Boolean, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database import Base
from typing import Optional


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model with UUID primary key."""

    __tablename__ = "users"

    # Additional fields beyond fastapi-users defaults
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # MVP Tax Spain profile fields
    vorname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    nachname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sprache: Mapped[str] = mapped_column(String(5), default="de", nullable=False)  # de, es, en
    telefonnummer: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="user", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    tax_cases: Mapped[list["TaxCase"]] = relationship("TaxCase", back_populates="user", cascade="all, delete-orphan")
    h7_forms: Mapped[list["H7FormData"]] = relationship("H7FormData", back_populates="user", cascade="all, delete-orphan")
    # NOTE: LifeChronicle relationship not needed here - we query entries directly via user_id

    def __repr__(self):
        return f"<User {self.email} (admin={self.is_admin})>"
