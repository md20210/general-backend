from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from pgvector.sqlalchemy import Vector
from ..database import Base


class Application(Base):
    """Job application record"""
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    position = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="uploaded", index=True)
    upload_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="applications")
    documents = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")
    status_history = relationship("ApplicationStatusHistory", back_populates="application", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Application(id={self.id}, company={self.company_name}, status={self.status})>"


class ApplicationDocument(Base):
    """Document associated with a job application"""
    __tablename__ = "application_documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=True)
    doc_type = Column(String(50), nullable=True)
    content = Column(Text, nullable=True)
    embedding = Column(Vector(384), nullable=True)
    indexed = Column(Boolean, nullable=True, default=False, server_default='false', index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    application = relationship("Application", back_populates="documents")

    def __repr__(self):
        return f"<ApplicationDocument(id={self.id}, filename={self.filename}, indexed={self.indexed})>"


class ApplicationStatusHistory(Base):
    """Track status changes for applications"""
    __tablename__ = "application_status_history"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    application = relationship("Application", back_populates="status_history")

    def __repr__(self):
        return f"<ApplicationStatusHistory(application_id={self.application_id}, {self.old_status} → {self.new_status})>"


class ApplicationChatMessage(Base):
    """Chat messages for application tracker"""
    __tablename__ = "application_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)
    message_metadata = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<ApplicationChatMessage(id={self.id}, role={self.role})>"
