"""Document Pydantic schemas."""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from backend.models.document import DocumentType


class DocumentBase(BaseModel):
    """Base document schema."""
    filename: Optional[str] = None
    url: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    type: DocumentType
    content: str
    project_id: Optional[UUID] = None


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    doc_metadata: Optional[Dict[str, Any]] = None


class DocumentRead(DocumentBase):
    """Schema for reading a document."""
    id: UUID
    user_id: UUID
    project_id: Optional[UUID]
    type: DocumentType
    content: str
    vector_collection_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadRequest(BaseModel):
    """Schema for file upload request metadata."""
    project_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentUrlRequest(BaseModel):
    """Schema for URL document request."""
    url: str = Field(..., description="URL to scrape")
    project_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentTextRequest(BaseModel):
    """Schema for text document request."""
    content: str = Field(..., min_length=1, description="Text content")
    title: Optional[str] = Field(None, max_length=255, description="Document title")
    project_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None
