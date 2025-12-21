"""Chat model."""
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
import enum

from backend.database import Base


class ChatRole(str, enum.Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Chat(Base):
    """Chat message model."""

    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    role: Mapped[ChatRole] = mapped_column(SQLEnum(ChatRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chats")
    project: Mapped["Project"] = relationship("Project", back_populates="chats")

    def __repr__(self):
        return f"<Chat {self.role}: {self.content[:50]}...>"
