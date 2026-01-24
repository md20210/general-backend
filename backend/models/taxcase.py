from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from pgvector.sqlalchemy import Vector
from ..database import Base


class TaxCase(Base):
    """Tax case record for document management and data extraction"""
    __tablename__ = "tax_cases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="created", index=True)  # created, processing, validated, confirmed
    validated = Column(Boolean, nullable=False, default=False, index=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="tax_cases")
    documents = relationship("TaxCaseDocument", back_populates="tax_case", cascade="all, delete-orphan")
    folders = relationship("TaxCaseFolder", back_populates="tax_case", cascade="all, delete-orphan")
    extracted_data = relationship("TaxCaseExtractedData", back_populates="tax_case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TaxCase(id={self.id}, name={self.name}, status={self.status})>"


class TaxCaseFolder(Base):
    """Hierarchical folder structure for tax case documents"""
    __tablename__ = "tax_case_folders"

    id = Column(Integer, primary_key=True, index=True)
    tax_case_id = Column(Integer, ForeignKey("tax_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("tax_case_folders.id", ondelete="CASCADE"), nullable=True, index=True)
    path = Column(String(2000), nullable=False, index=True)
    level = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tax_case = relationship("TaxCase", back_populates="folders")
    parent = relationship("TaxCaseFolder", remote_side=[id], backref="children")
    documents = relationship("TaxCaseDocument", back_populates="folder")

    def __repr__(self):
        return f"<TaxCaseFolder(id={self.id}, path={self.path})>"


class TaxCaseDocument(Base):
    """Document associated with a tax case"""
    __tablename__ = "tax_case_documents"

    id = Column(Integer, primary_key=True, index=True)
    tax_case_id = Column(Integer, ForeignKey("tax_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    folder_id = Column(Integer, ForeignKey("tax_case_folders.id", ondelete="CASCADE"), nullable=True, index=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=True)
    doc_type = Column(String(50), nullable=True)
    content = Column(Text, nullable=True)  # Extracted text content
    embedding = Column(Vector(384), nullable=True)
    validated = Column(Boolean, nullable=False, default=False, index=True)  # Status: Validiert

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tax_case = relationship("TaxCase", back_populates="documents")
    folder = relationship("TaxCaseFolder", back_populates="documents")

    def __repr__(self):
        return f"<TaxCaseDocument(id={self.id}, filename={self.filename}, validated={self.validated})>"


class TaxCaseExtractedData(Base):
    """Structured data extracted from tax case documents using LLM"""
    __tablename__ = "tax_case_extracted_data"

    id = Column(Integer, primary_key=True, index=True)
    tax_case_id = Column(Integer, ForeignKey("tax_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("tax_case_documents.id", ondelete="CASCADE"), nullable=True, index=True)

    # Extracted fields (flexible structure)
    field_name = Column(String(255), nullable=False, index=True)  # e.g., "name", "phone_number", "order_position"
    field_value = Column(Text, nullable=False)
    field_type = Column(String(50), nullable=True)  # text, number, date, email, phone, etc.
    confidence = Column(Float, nullable=True)  # Confidence score from LLM

    # User validation
    confirmed = Column(Boolean, nullable=False, default=False, index=True)
    edited = Column(Boolean, nullable=False, default=False)  # Was this manually edited?
    original_value = Column(Text, nullable=True)  # Original value before editing

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tax_case = relationship("TaxCase", back_populates="extracted_data")
    document = relationship("TaxCaseDocument")

    def __repr__(self):
        return f"<TaxCaseExtractedData(id={self.id}, field_name={self.field_name}, confirmed={self.confirmed})>"
