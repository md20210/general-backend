"""Chat schemas for request/response."""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class InMemoryDocument(BaseModel):
    """In-memory document for RAG without database storage."""
    filename: str = Field(..., description="Document filename (e.g., 'CV.pdf', 'Requirements.docx')")
    content: str = Field(..., min_length=1, description="Full document text content")
    type: str = Field(..., description="Document type (e.g., 'employer', 'applicant', 'cv', 'requirements')")


class ChatMessageRequest(BaseModel):
    """Request schema for chat message."""
    message: str = Field(..., min_length=1, description="User's question/message")
    project_id: Optional[UUID] = Field(None, description="Project ID to scope document search (database RAG)")
    system_context: Optional[str] = Field(None, description="Additional context (e.g., match result summary)")
    documents: Optional[List[InMemoryDocument]] = Field(
        None,
        description="Optional in-memory documents for RAG (bypasses database). Use for CV Matcher."
    )
    provider: Optional[str] = Field("ollama", description="LLM provider (ollama, grok, anthropic)")
    model: Optional[str] = Field(None, description="Model name (provider-specific)")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(500, ge=1, le=2000, description="Max tokens to generate")
    context_limit: Optional[int] = Field(3, ge=1, le=10, description="Number of documents/chunks to retrieve")


class DocumentSource(BaseModel):
    """Source document that was used for RAG."""
    document_id: str
    filename: Optional[str] = None
    type: str
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")


class ChatMessageResponse(BaseModel):
    """Response schema for chat message."""
    message: str = Field(..., description="AI-generated response")
    sources: List[DocumentSource] = Field(default_factory=list, description="Source documents used")
    model: str = Field(..., description="Model that generated the response")
    provider: str = Field(..., description="Provider that was used")
