"""Project Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from backend.models.project import ProjectType


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    type: ProjectType
    config: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class ProjectRead(ProjectBase):
    """Schema for reading a project."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
