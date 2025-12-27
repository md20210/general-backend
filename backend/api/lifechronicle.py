"""LifeChronicle API endpoints with PostgreSQL backend."""
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import date
from pathlib import Path
import os
import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.dependencies import current_active_user
from backend.models.user import User
from backend.models.lifechronicle import LifeChronicleEntry
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

logger = logging.getLogger(__name__)
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
                # TEMPORARILY DISABLED until RAILWAY_VOLUME_NAME is set
                # try:
                #     with open(file_path, "wb") as f:
                #         f.write(content)
                #
                #     # Extract EXIF metadata from file
                #     photo_metadata = extract_photo_metadata(file_path)
                #     photo_metadata_list.append(photo_metadata)
                #
                #     # Store relative URL (for volume-based storage)
                #     photo_urls.append(f"/uploads/lifechronicle/{unique_name}")
                # except Exception as e:
                #     logger.warning(f"Could not save photo to disk: {e}")

                # For now: Skip file storage, use Base64 only
                pass

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

        # TEMPORARY: Use Base64 data URLs (file storage disabled)
        # TODO: Re-enable file storage when RAILWAY_VOLUME_NAME is set
        if photos_base64:
            photo_urls = [p["data_url"] for p in photos_base64]
            logger.info(f"Using {len(photo_urls)} Base64 data URLs (file storage disabled)")

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


@router.post("/entries/{entry_id}/process", response_model=EntryResponse)
async def process_entry(
    entry_id: UUID,
    provider: str = "ollama",
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Process entry with LLM to create literary book chapter.

    Args:
        entry_id: Entry UUID
        provider: LLM provider ("ollama", "grok", or "anthropic")
        db: Database session
        user: Current authenticated user

    Returns:
        Updated entry with refined_text

    Raises:
        404: Entry not found or unauthorized
    """
    try:
        # Get entry
        entry = await lifechronicle_db_service.get_entry(db, entry_id, user.id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")

        # Create prompt for LLM
        prompt = f"""Du bist ein professioneller Autobiografie-Autor.

Verwandle die folgende persönliche Erinnerung in ein literarisches Buchkapitel.
Schreibe in der Ich-Form, emotional und lebendig. Füge sensorische Details hinzu.
Länge: 3-5 Sätze.

Datum: {entry.entry_date}
Erinnerung: {entry.original_text}

Buchkapitel:"""

        # Process with LLM
        from backend.services.llm_gateway import llm_gateway

        if provider == "grok":
            result = llm_gateway.generate(
                prompt=prompt,
                provider="grok",
                model="grok-beta",
                temperature=0.7,
                max_tokens=300
            )
        elif provider == "anthropic":
            result = llm_gateway.generate(
                prompt=prompt,
                provider="anthropic",
                model="claude-sonnet-3-5-20241022",
                temperature=0.7,
                max_tokens=300
            )
        else:  # ollama (default)
            result = llm_gateway.generate(
                prompt=prompt,
                provider="ollama",
                model="qwen2.5:3b",
                temperature=0.7,
                max_tokens=300
            )

        refined_text = result.get('response', '').strip()

        # Update entry with refined text
        updated_entry = await lifechronicle_db_service.mark_as_refined(
            db, entry_id, user.id, refined_text
        )

        if not updated_entry:
            raise HTTPException(status_code=404, detail="Entry not found")

        return EntryResponse(success=True, entry=updated_entry)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process entry: {str(e)}")


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
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors as rl_colors
        from fastapi.responses import Response
        import html
        import base64
        from PIL import Image as PILImage

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

            # Add photos if available (Base64 Data URLs)
            if entry.photo_urls:
                photo_elements = []
                for photo_url in entry.photo_urls[:3]:  # Max 3 photos per entry
                    try:
                        if photo_url.startswith('data:image'):
                            # Extract Base64 data from data URL
                            # Format: data:image/jpeg;base64,/9j/4AAQ...
                            header, base64_data = photo_url.split(',', 1)

                            # Decode Base64 to bytes
                            image_data = base64.b64decode(base64_data)

                            # Create PIL Image from bytes
                            pil_image = PILImage.open(BytesIO(image_data))

                            # Save to temporary BytesIO for ReportLab
                            img_buffer = BytesIO()
                            pil_image.save(img_buffer, format='JPEG')
                            img_buffer.seek(0)

                            # Create ReportLab Image with max width 5cm
                            rl_image = RLImage(img_buffer, width=5*cm, height=5*cm)
                            photo_elements.append(rl_image)
                    except Exception as e:
                        logger.warning(f"Failed to process photo for PDF: {e}")
                        continue

                # Add photos in a row if any were processed
                if photo_elements:
                    photo_table = Table([photo_elements], colWidths=[5*cm]*len(photo_elements))
                    elements.append(photo_table)

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


@router.post("/migrate-photos")
async def migrate_photos(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Migrate old file-path photo entries to Base64 data URLs.

    For entries with file paths in photo_urls (/uploads/...):
    - If Base64 data exists in entry_metadata.photos_base64, use it
    - Otherwise, clear the photo_urls

    Args:
        db: Database session
        user: Current authenticated user

    Returns:
        Migration summary
    """
    try:
        from sqlalchemy import select

        # Get all user entries
        result = await db.execute(
            select(LifeChronicleEntry)
            .where(LifeChronicleEntry.user_id == user.id)
        )
        entries = result.scalars().all()

        updated_count = 0
        cleared_count = 0
        skipped_count = 0

        for entry in entries:
            if not entry.photo_urls:
                continue

            # Check if any photo_urls are file paths
            has_file_paths = any(url.startswith("/uploads") for url in entry.photo_urls)

            if has_file_paths:
                logger.info(f"Migrating entry: {entry.title} ({entry.id})")

                # Check if Base64 data exists in metadata
                metadata = entry.entry_metadata or {}
                photos_base64 = metadata.get("photos_base64", [])

                if photos_base64:
                    # Extract Base64 data URLs
                    base64_urls = [p["data_url"] for p in photos_base64]
                    entry.photo_urls = base64_urls
                    logger.info(f"  → Updated to Base64 ({len(base64_urls)} photos)")
                    updated_count += 1
                else:
                    # No Base64 data available - clear photos
                    entry.photo_urls = []
                    logger.info(f"  → No Base64 data - cleared photos")
                    cleared_count += 1
            else:
                skipped_count += 1

        # Commit all changes
        await db.commit()

        return {
            "success": True,
            "message": "Photo migration complete",
            "updated_to_base64": updated_count,
            "cleared_no_data": cleared_count,
            "already_base64": skipped_count,
            "total_processed": updated_count + cleared_count
        }

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")
