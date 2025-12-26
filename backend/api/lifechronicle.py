"""LifeChronicle API endpoints with PostgreSQL backend."""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import date
from pathlib import Path
import os
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import current_active_user
from backend.models.user import User
from backend.database import get_async_session
from backend.services.lifechronicle_db_service import lifechronicle_db_service
from backend.services.photo_metadata import extract_photo_metadata
from backend.schemas.lifechronicle import (
    LifeChronicleEntryCreate,
    LifeChronicleEntryUpdate,
    LifeChronicleEntryResponse,
    EntryListResponse,
    EntryResponse,
)


router = APIRouter(prefix="/lifechronicle", tags=["LifeChronicle"])

# Photo upload configuration
UPLOAD_DIR = Path("/app/uploads/lifechronicle")  # Railway Volume path
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
    db: AsyncSession = Depends(get_async_session),
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
    db: AsyncSession = Depends(get_async_session),
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
    title: str = Form(...),
    date: str = Form(...),  # Will be parsed as date
    text: str = Form(...),
    photos: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Create a new timeline entry with optional photos.

    Supports both:
    - JSON (no photos): POST with Content-Type: application/json
    - Multipart (with photos): POST with Content-Type: multipart/form-data

    Args:
        title: Entry title
        date: Entry date (YYYY-MM-DD)
        text: Original entry text
        photos: Optional list of photo files (max 5)
        db: Database session
        user: Current authenticated user

    Returns:
        Created entry with photo URLs if photos uploaded
    """
    try:
        # Validate date format
        try:
            entry_date = date  # Keep as string for now, backend will parse
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Validate photo count
        if photos and len(photos) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 photos allowed")

        # Save photos to disk and extract metadata
        photo_urls = []
        photo_metadata_list = []
        if photos:
            for photo in photos:
                # Generate unique filename
                file_ext = os.path.splitext(photo.filename)[1]
                unique_name = f"{uuid4()}{file_ext}"
                file_path = UPLOAD_DIR / unique_name

                # Save file
                with open(file_path, "wb") as f:
                    content = await photo.read()
                    f.write(content)

                # Extract EXIF metadata
                photo_metadata = extract_photo_metadata(file_path)
                photo_metadata_list.append(photo_metadata)

                # Store relative URL
                photo_urls.append(f"/uploads/lifechronicle/{unique_name}")

        # Create entry using Pydantic schema
        entry_data = LifeChronicleEntryCreate(
            title=title,
            entry_date=entry_date,  # Use entry_date (not date)
            original_text=text
        )

        # Build entry_metadata with photo metadata
        entry_metadata = {}
        if photo_metadata_list:
            entry_metadata["photos"] = photo_metadata_list

        entry = await lifechronicle_db_service.create_entry(
            db, user.id, entry_data, photo_urls, entry_metadata or None
        )
        return EntryResponse(success=True, entry=entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")


@router.patch("/entries/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: UUID,
    entry_data: LifeChronicleEntryUpdate,
    db: AsyncSession = Depends(get_async_session),
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
    db: AsyncSession = Depends(get_async_session),
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
