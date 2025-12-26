"""LifeChronicle model for timeline entries."""
from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date as date_type
from uuid import uuid4

from backend.database import Base


class LifeChronicleEntry(Base):
    """LifeChronicle entry model for storing life timeline entries."""

    __tablename__ = "lifechronicle_entries"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    refined_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_urls: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    entry_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    is_refined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    # NOTE: No back_populates to avoid circular repr() recursion with User
    user: Mapped["User"] = relationship("User")

    def __repr__(self):
        return f"<LifeChronicleEntry {self.title} ({self.date})>"
