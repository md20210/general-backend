"""LifeChronicle Pydantic schemas."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID


class LifeChronicleEntryBase(BaseModel):
    """Base schema for LifeChronicle entry."""
    title: str = Field(..., min_length=1, max_length=255, description="Entry title")
    date: date = Field(..., description="Date of the event (YYYY-MM-DD)")
    original_text: str = Field(..., min_length=1, description="Original user-written text")


class LifeChronicleEntryCreate(LifeChronicleEntryBase):
    """Schema for creating a new entry."""
    pass


class LifeChronicleEntryUpdate(BaseModel):
    """Schema for updating an entry."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    date: Optional[date] = None
    original_text: Optional[str] = Field(None, min_length=1)
    refined_text: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    entry_metadata: Optional[Dict[str, Any]] = None


class LifeChronicleEntryResponse(LifeChronicleEntryBase):
    """Schema for entry response."""
    id: UUID
    user_id: UUID
    refined_text: Optional[str] = None
    photo_urls: Optional[List[str]] = None
    entry_metadata: Optional[Dict[str, Any]] = None
    is_refined: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProcessEntryRequest(BaseModel):
    """Request schema for LLM processing."""
    provider: str = Field(default="ollama", description="LLM provider: ollama, grok, or anthropic")


class EntryListResponse(BaseModel):
    """Response schema for list of entries."""
    success: bool = True
    entries: List[LifeChronicleEntryResponse]
    total: int


class EntryResponse(BaseModel):
    """Response schema for single entry."""
    success: bool = True
    entry: LifeChronicleEntryResponse
