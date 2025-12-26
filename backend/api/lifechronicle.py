"""LifeChronicle API endpoints with PostgreSQL backend."""
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import current_active_user
from backend.models.user import User
from backend.database import get_async_db
from backend.services.lifechronicle_db_service import lifechronicle_db_service
from backend.schemas.lifechronicle import (
    LifeChronicleEntryCreate,
    LifeChronicleEntryUpdate,
    LifeChronicleEntryResponse,
    EntryListResponse,
    EntryResponse,
)


router = APIRouter(prefix="/lifechronicle", tags=["LifeChronicle"])


@router.get("/health")
async def health_check():
    """Health check endpoint for LifeChronicle service."""
    return {
        "status": "healthy",
        "service": "lifechronicle",
        "version": "2.0.0",
        "database": "postgresql"
    }


@router.get("/entries", response_model=EntryListResponse)
async def get_entries(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user)
):
    """
    Get all timeline entries for the current user.

    Returns chronologically sorted list (newest first).

    Args:
        skip: Number of entries to skip (pagination)
        limit: Maximum entries to return
        db: Database session
        user: Current authenticated user

    Returns:
        List of timeline entries
    """
    entries = await lifechronicle_db_service.get_all_entries(db, user.id, skip, limit)
    return EntryListResponse(
        success=True,
        entries=entries,
        total=len(entries)
    )


@router.get("/entries/{entry_id}", response_model=EntryResponse)
async def get_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user)
):
    """
    Get a single timeline entry by ID.

    Args:
        entry_id: Entry UUID
        db: Database session
        user: Current authenticated user

    Returns:
        Single entry

    Raises:
        404: Entry not found or unauthorized
    """
    entry = await lifechronicle_db_service.get_entry(db, entry_id, user.id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return EntryResponse(success=True, entry=entry)


@router.post("/entries", response_model=EntryResponse, status_code=201)
async def create_entry(
    entry_data: LifeChronicleEntryCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user)
):
    """
    Create a new timeline entry.

    Args:
        entry_data: Entry data (title, date, original_text)
        db: Database session
        user: Current authenticated user

    Returns:
        Created entry with pending refinement status
    """
    try:
        entry = await lifechronicle_db_service.create_entry(db, user.id, entry_data)
        return EntryResponse(success=True, entry=entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")


@router.patch("/entries/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: UUID,
    entry_data: LifeChronicleEntryUpdate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user)
):
    """
    Update an existing timeline entry.

    Args:
        entry_id: Entry UUID
        entry_data: Fields to update
        db: Database session
        user: Current authenticated user

    Returns:
        Updated entry

    Raises:
        404: Entry not found or unauthorized
    """
    entry = await lifechronicle_db_service.update_entry(db, entry_id, user.id, entry_data)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return EntryResponse(success=True, entry=entry)


@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(current_active_user)
):
    """
    Delete a timeline entry.

    Args:
        entry_id: Entry UUID
        db: Database session
        user: Current authenticated user

    Returns:
        Success message

    Raises:
        404: Entry not found or unauthorized
    """
    deleted = await lifechronicle_db_service.delete_entry(db, entry_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {"success": True, "message": "Entry deleted"}
