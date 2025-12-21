"""Project model."""
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
import enum

from backend.database import Base


class ProjectType(str, enum.Enum):
    """Project types."""
    CV_MATCHER = "cv_matcher"
    PRIVATE_GPT = "private_gpt"
    TELL_ME_LIFE = "tell_me_life"
    OTHER = "other"


class Project(Base):
    """Project model for organizing user work."""

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[ProjectType] = mapped_column(SQLEnum(ProjectType), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    config: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="projects")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="project", cascade="all, delete-orphan")
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name} ({self.type})>"
