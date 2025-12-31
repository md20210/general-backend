"""Document model."""
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import uuid4
import enum
from pgvector.sqlalchemy import Vector

from backend.database import Base


class DocumentType(str, enum.Enum):
    """Document types."""
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    URL = "url"
    TEXT = "text"
    CV_SHOWCASE = "cv_showcase"


class Document(Base):
    """Document model for storing uploaded files and URLs."""

    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    type: Mapped[DocumentType] = mapped_column(SQLEnum(DocumentType), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    doc_metadata: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    embedding: Mapped[Vector] = mapped_column(Vector(384), nullable=True)  # sentence-transformers default size
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="documents")
    project: Mapped["Project"] = relationship("Project", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.filename or self.url or 'text'} ({self.type})>"
