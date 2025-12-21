"""Match model for CV Matcher."""
from sqlalchemy import String, Text, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4

from backend.database import Base


class Match(Base):
    """CV Match result model."""

    __tablename__ = "matches"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)

    # Document references
    employer_doc_ids: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    applicant_doc_ids: Mapped[list] = mapped_column(ARRAY(String), nullable=False)

    # LLM info
    llm_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Match results
    match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    comparison: Mapped[dict] = mapped_column(JSONB, nullable=False)
    strengths: Mapped[list] = mapped_column(ARRAY(Text), nullable=False)
    gaps: Mapped[list] = mapped_column(ARRAY(Text), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[list] = mapped_column(ARRAY(Text), nullable=True)
    target_position: Mapped[str] = mapped_column(String(255), nullable=True)
    experience_years: Mapped[int] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="matches")
    project: Mapped["Project"] = relationship("Project", back_populates="matches")

    def __repr__(self):
        return f"<Match {self.id} (score={self.match_score})>"
