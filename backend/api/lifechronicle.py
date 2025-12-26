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
# Use relative path for local dev, /app/uploads for Railway production
import os
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads/lifechronicle"))
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
    photos: List[UploadFile] = File(None),
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
        # Parse date string to date object for Pydantic validation
        from datetime import datetime
        try:
            entry_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        # Normalize photos to empty list if None
        if photos is None:
            photos = []

        # Validate photo count
        if len(photos) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 photos allowed")

        # Save photos to disk and extract metadata
        photo_urls = []
        photo_metadata_list = []
        photos_base64 = []  # Base64 fallback for Railway (no volume)

        if photos:
            import base64
            for photo in photos:
                # Read photo content ONCE
                content = await photo.read()

                # Generate unique filename
                file_ext = os.path.splitext(photo.filename)[1]
                unique_name = f"{uuid4()}{file_ext}"
                file_path = UPLOAD_DIR / unique_name

                # Try to save file to disk (works if volume mounted)
                try:
                    with open(file_path, "wb") as f:
                        f.write(content)

                    # Extract EXIF metadata from file
                    photo_metadata = extract_photo_metadata(file_path)
                    photo_metadata_list.append(photo_metadata)

                    # Store relative URL (for volume-based storage)
                    photo_urls.append(f"/uploads/lifechronicle/{unique_name}")
                except Exception as e:
                    logger.warning(f"Could not save photo to disk: {e}")

                # ALWAYS save as Base64 (fallback for Railway without volume)
                # Detect content type
                content_type = "image/jpeg"
                if file_ext.lower() in ['.png']:
                    content_type = "image/png"
                elif file_ext.lower() in ['.heic', '.heif']:
                    content_type = "image/heic"

                # Create data URL
                b64_data = base64.b64encode(content).decode('utf-8')
                data_url = f"data:{content_type};base64,{b64_data}"
                photos_base64.append({
                    "filename": photo.filename,
                    "data_url": data_url,
                    "size_bytes": len(content)
                })

        # Create entry using Pydantic schema
        entry_data = LifeChronicleEntryCreate(
            title=title,
            entry_date=entry_date,  # Use entry_date (not date)
            original_text=text
        )

        # Build entry_metadata with photo metadata AND base64 data
        entry_metadata = {}
        if photo_metadata_list:
            entry_metadata["photos"] = photo_metadata_list
        if photos_base64:
            entry_metadata["photos_base64"] = photos_base64  # Fallback for Railway

        # TEMPORARY: Always use Base64 until Railway Volume is configured
        # TODO: Remove this when RAILWAY_VOLUME_NAME is set
        if photos_base64:
            photo_urls = [p["data_url"] for p in photos_base64]
            logger.info("Using Base64 data URLs (RAILWAY_VOLUME_NAME not configured)")

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


@router.get("/export/pdf")
async def export_pdf(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Export user's entire timeline as PDF book.

    Creates beautifully formatted PDF with:
    - Title page
    - Chronological chapters (oldest to newest)
    - Uses refined text where available
    - Colored chapter boxes (timeline colors)

    Args:
        db: Database session
        user: Current authenticated user

    Returns:
        PDF file as binary stream
    """
    try:
        # Get all user entries sorted chronologically (oldest first for book)
        entries = await lifechronicle_db_service.get_all_entries(db, user.id, skip=0, limit=1000)
        entries.sort(key=lambda x: x.entry_date)

        # Generate PDF
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors as rl_colors
        from fastapi.responses import Response
        import html

        # Timeline color palette (same as frontend)
        TIMELINE_COLORS = [
            {'bg': rl_colors.HexColor('#e9d5ff'), 'border': rl_colors.HexColor('#c084fc'), 'text': rl_colors.HexColor('#581c87')},  # Purple
            {'bg': rl_colors.HexColor('#ccfbf1'), 'border': rl_colors.HexColor('#5eead4'), 'text': rl_colors.HexColor('#134e4a')},  # Teal
            {'bg': rl_colors.HexColor('#d1fae5'), 'border': rl_colors.HexColor('#6ee7b7'), 'text': rl_colors.HexColor('#065f46')},  # Green
            {'bg': rl_colors.HexColor('#fef3c7'), 'border': rl_colors.HexColor('#fcd34d'), 'text': rl_colors.HexColor('#78350f')},  # Yellow
            {'bg': rl_colors.HexColor('#fed7aa'), 'border': rl_colors.HexColor('#fdba74'), 'text': rl_colors.HexColor('#7c2d12')},  # Orange
            {'bg': rl_colors.HexColor('#fce7f3'), 'border': rl_colors.HexColor('#f9a8d4'), 'text': rl_colors.HexColor('#831843')},  # Pink
        ]

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elements = []

        # Title Page
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=rl_colors.HexColor('#14b8a6'),  # Teal
            spaceAfter=12,
            alignment=1  # Center
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=rl_colors.gray,
            spaceAfter=30,
            alignment=1  # Center
        )

        elements.append(Spacer(1, 5*cm))
        elements.append(Paragraph("Meine Lebensgeschichte", title_style))
        elements.append(Paragraph("Eine persönliche Chronik", subtitle_style))
        elements.append(Spacer(1, 10*cm))

        # Entry chapters
        for idx, entry in enumerate(entries):
            color = TIMELINE_COLORS[idx % len(TIMELINE_COLORS)]

            # Title with colored background (escape HTML)
            title_text = html.escape(f"{entry.entry_date.year} - {entry.title}")
            title_para = Paragraph(title_text, ParagraphStyle(
                'EntryTitle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=color['text'],
                spaceAfter=6
            ))

            # Text (refined if available, otherwise original) - ESCAPE HTML
            text_content = entry.refined_text or entry.original_text
            text_content_escaped = html.escape(text_content).replace('\n', '<br/>')
            text_para = Paragraph(text_content_escaped, styles['BodyText'])

            # Create colored table box
            table = Table([[title_para], [text_para]], colWidths=[15*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), color['bg']),
                ('TEXTCOLOR', (0, 0), (0, 0), color['text']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 3, color['border']),
                ('LINEABOVE', (0, 1), (-1, 1), 1, color['border']),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 1*cm))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=my-life-chronicle.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")
