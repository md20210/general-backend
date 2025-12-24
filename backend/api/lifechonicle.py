"""LifeChronicle API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
import uuid

from backend.services.lifechonicle_service import lifechonicle_service


router = APIRouter(prefix="/lifechonicle", tags=["LifeChronicle"])


class TimelineEntry(BaseModel):
    """Timeline entry model."""
    id: str
    date: str
    original_text: str
    processed_text: Optional[str] = None
    status: str  # 'pending' or 'processed'
    created_at: str


class CreateEntryRequest(BaseModel):
    """Create timeline entry request."""
    date: str
    original_text: str


class EntryResponse(BaseModel):
    """Single entry response."""
    success: bool
    entry: TimelineEntry


class EntriesResponse(BaseModel):
    """Multiple entries response."""
    success: bool
    entries: List[TimelineEntry]


@router.get("/entries", response_model=EntriesResponse)
async def get_entries():
    """
    Get all timeline entries for test user.

    Returns chronologically sorted list of all life events.
    """
    try:
        entries = lifechonicle_service.get_all_entries()
        return EntriesResponse(success=True, entries=entries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/entries", response_model=EntryResponse)
async def create_entry(request: CreateEntryRequest):
    """
    Create new timeline entry.

    Args:
        request: Entry data with date and original_text

    Returns:
        Created entry with pending status
    """
    try:
        entry = lifechonicle_service.create_entry(
            date=request.date,
            original_text=request.original_text
        )
        return EntryResponse(success=True, entry=entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str):
    """Delete timeline entry by ID."""
    try:
        deleted = lifechonicle_service.delete_entry(entry_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Entry not found")

        return {"success": True, "message": "Entry deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/entries/{entry_id}/process", response_model=EntryResponse)
async def process_entry(entry_id: str):
    """
    Process entry with local LLM to create literary book chapter.

    Uses Ollama (llama3 or mistral) to transform raw life story
    into a beautifully written book chapter.

    Args:
        entry_id: ID of entry to process

    Returns:
        Updated entry with processed_text and status='processed'
    """
    try:
        entry = await lifechonicle_service.process_with_llm(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")

        return EntryResponse(success=True, entry=entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {str(e)}")


@router.get("/export/pdf")
async def export_pdf():
    """
    Export entire timeline as PDF book.

    Creates beautifully formatted PDF with all entries
    (using processed text where available).

    Returns:
        PDF file as binary stream
    """
    try:
        pdf_bytes = await lifechonicle_service.export_as_pdf()

        from fastapi.responses import Response
        return Response(
            content=pdf_bytes.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=my-life-chronicle.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")
