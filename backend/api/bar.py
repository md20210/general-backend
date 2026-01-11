"""
Bar API Endpoints for Ca l'Elena Bar Website
Public and Admin endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.bar_service import BarService
from backend.services.bar_team_service import BarTeamService
from backend.services.email_service import email_service
from backend.services.document_summary_service import DocumentSummaryService
from backend.services.vector_service import VectorService
from backend.services.llm_translation_service import LLMTranslationService
from backend.services.bar_elasticsearch_service import bar_es_service
from backend.schemas.bar import (
    BarInfoResponse, BarInfoUpdate, BarMenuResponse, BarMenuCreate,
    BarNewsResponse, BarNewsCreate, BarReservationResponse, BarReservationCreate,
    BarNewsletterResponse, BarNewsletterCreate, AdminLoginRequest, AdminLoginResponse,
    LLMSelectRequest, LLMSelectResponse, BarSettingsResponse, BarSettingsUpdate,
    BarTeamResponse, BarTeamCreate, BarTeamUpdate
)
from backend.models.bar import BarSettings, BarMenu
from typing import List
import os
import base64
from datetime import datetime, timedelta
from jose import jwt, JWTError

router = APIRouter(prefix="/bar", tags=["bar"])

# Simple admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "senior"
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "bar-ca-l-elena-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

security = HTTPBearer()

# In-memory LLM selection (can be moved to DB later)
selected_llm = {"provider": "ollama"}  # Default to GDPR-compliant ollama


def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username != ADMIN_USERNAME:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return username
    except JWTError as e:
        if "expired" in str(e).lower():
            raise HTTPException(status_code=401, detail="Token expired")
        raise HTTPException(status_code=401, detail="Invalid token")


# ========== PUBLIC ENDPOINTS ==========

@router.get("/info", response_model=BarInfoResponse, summary="Get bar general information")
async def get_bar_info(db: Session = Depends(get_db)):
    """
    Get general bar information (address, hours, description, etc.)
    Public endpoint - no authentication required
    """
    bar_info = BarService.get_bar_info(db)
    if not bar_info:
        # Initialize with default data if not exists
        bar_info = BarService.initialize_bar_data(db)
    return bar_info


@router.get("/menus", response_model=List[BarMenuResponse], summary="Get all active menus")
async def get_menus(db: Session = Depends(get_db)):
    """
    Get all active menus (lunch, food, drinks)
    Public endpoint - no authentication required
    """
    return BarService.get_all_menus(db, active_only=True)


@router.get("/news", response_model=List[BarNewsResponse], summary="Get published news and events")
async def get_news(db: Session = Depends(get_db)):
    """
    Get all published news and announcements
    Public endpoint - no authentication required
    """
    return BarService.get_all_news(db, published_only=True)


@router.get("/settings/public", summary="Get public settings")
async def get_public_settings(db: Session = Depends(get_db)):
    """
    Get public-facing settings (auto-speak enabled)
    Public endpoint - no authentication required
    """
    settings = BarService.get_settings(db)
    if not settings:
        return {"auto_speak_enabled": True}
    return {
        "auto_speak_enabled": settings.auto_speak_enabled
    }


@router.post("/reservations", response_model=BarReservationResponse, summary="Create reservation", status_code=status.HTTP_201_CREATED)
async def create_reservation(
    reservation: BarReservationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new reservation
    Public endpoint - no authentication required
    """
    return BarService.create_reservation(db, reservation)


@router.post("/newsletter", response_model=BarNewsletterResponse, summary="Subscribe to newsletter", status_code=status.HTTP_201_CREATED)
async def subscribe_newsletter(
    subscription: BarNewsletterCreate,
    db: Session = Depends(get_db)
):
    """
    Subscribe to newsletter
    Public endpoint - no authentication required
    """
    return BarService.subscribe_newsletter(db, subscription)


# ========== ADMIN ENDPOINTS ==========

@router.post("/admin/login", response_model=AdminLoginResponse, summary="Admin login")
async def admin_login(credentials: AdminLoginRequest):
    """
    Admin login endpoint
    Returns JWT token for admin operations
    """
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": credentials.username})
    return AdminLoginResponse(access_token=access_token)


@router.get("/admin/llm-select", response_model=LLMSelectResponse, summary="Get selected LLM provider")
async def get_llm_selection(admin: str = Depends(verify_admin_token)):
    """
    Get currently selected LLM provider (ollama or grok)
    Requires admin authentication
    """
    return LLMSelectResponse(
        llm_provider=selected_llm["provider"],
        message=f"Currently using: {selected_llm['provider']}"
    )


@router.post("/admin/llm-select", response_model=LLMSelectResponse, summary="Select LLM provider")
async def select_llm_provider(
    request: LLMSelectRequest,
    admin: str = Depends(verify_admin_token)
):
    """
    Select LLM provider for chatbot (ollama for GDPR, grok for speed)
    Requires admin authentication
    """
    selected_llm["provider"] = request.llm_provider
    return LLMSelectResponse(
        llm_provider=request.llm_provider,
        message=f"LLM provider changed to: {request.llm_provider}"
    )


@router.put("/admin/info", response_model=BarInfoResponse, summary="Update bar information")
async def update_bar_info(
    bar_data: BarInfoUpdate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Update bar general information
    Requires admin authentication
    """
    return BarService.create_or_update_bar_info(db, bar_data)


@router.post("/admin/reinitialize-data", response_model=BarInfoResponse, summary="Reinitialize bar data with defaults")
async def reinitialize_bar_data(
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Reinitialize bar data with default multilingual values
    This will reset bar info including reviews to the default structure
    Requires admin authentication
    """
    return BarService.initialize_bar_data(db, force=True)


@router.post("/admin/upload-menu", response_model=BarMenuResponse, summary="Upload menu document", status_code=status.HTTP_201_CREATED)
async def upload_menu(
    title: str = Form(...),
    menu_type: str = Form(..., regex="^(lunch|food|drinks|other)$"),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Upload menu document (PDF/DOCX)
    Processes document with document_summary_service and stores in vector DB
    Requires admin authentication
    """
    try:
        # Read file content
        file_content = await file.read()

        # Save to uploads directory
        upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"menu_{datetime.utcnow().timestamp()}_{file.filename}")

        with open(file_path, "wb") as f:
            f.write(file_content)

        # Process document with document_summary_service
        # This would extract text and create embeddings
        # For now, we'll create a menu entry with file reference

        menu_data = BarMenuCreate(
            title=title,
            description=description,
            menu_type=menu_type,
            document_url=f"/uploads/{os.path.basename(file_path)}",
            display_order=0
        )

        menu = BarService.create_menu(db, menu_data)

        return menu

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/admin/news", response_model=BarNewsResponse, summary="Create news/announcement", status_code=status.HTTP_201_CREATED)
async def create_news(
    news: BarNewsCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Create news or announcement
    Requires admin authentication
    """
    return BarService.create_news(db, news)


@router.put("/admin/news/{news_id}", response_model=BarNewsResponse, summary="Update news")
async def update_news(
    news_id: int,
    news: BarNewsCreate,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Update news/announcement
    Requires admin authentication
    """
    updated = BarService.update_news(db, news_id, news)
    if not updated:
        raise HTTPException(status_code=404, detail="News not found")
    return updated


@router.delete("/admin/news/{news_id}", summary="Delete news", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Delete news/announcement
    Requires admin authentication
    """
    success = BarService.delete_news(db, news_id)
    if not success:
        raise HTTPException(status_code=404, detail="News not found")


@router.delete("/admin/menus/{menu_id}", summary="Delete menu", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Delete menu
    Requires admin authentication
    """
    success = BarService.delete_menu(db, menu_id)
    if not success:
        raise HTTPException(status_code=404, detail="Menu not found")


@router.get("/admin/reservations", response_model=List[BarReservationResponse], summary="Get all reservations")
async def get_all_reservations(
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Get all reservations (admin view)
    Requires admin authentication
    """
    return BarService.get_all_reservations(db)


@router.put("/admin/reservations/{reservation_id}/status", response_model=BarReservationResponse, summary="Update reservation status")
async def update_reservation_status(
    reservation_id: int,
    status: str = Form(..., regex="^(pending|confirmed|cancelled)$"),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Update reservation status (pending/confirmed/cancelled)
    Requires admin authentication
    """
    updated = BarService.update_reservation_status(db, reservation_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return updated


@router.get("/admin/newsletter", response_model=List[BarNewsletterResponse], summary="Get newsletter subscribers")
async def get_newsletter_subscribers(
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Get all newsletter subscribers
    Requires admin authentication
    """
    return BarService.get_all_subscribers(db)


# ===== Bar Settings Endpoints =====

@router.get("/admin/settings", summary="Get bar settings")
async def get_bar_settings(
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Get current bar settings (LLM provider, contact email, etc.)
    Requires admin authentication
    """
    from backend.models.bar import BarSettings
    settings = db.query(BarSettings).first()
    if not settings:
        # Create default settings
        settings = BarSettings(
            llm_provider="ollama",
            ollama_model="llama3.2:3b",
            auto_speak_enabled=True
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/admin/settings", summary="Update bar settings")
async def update_bar_settings(
    llm_provider: str = Form(None, regex="^(ollama|grok)$"),
    grok_api_key: str = Form(None),
    ollama_model: str = Form(None),
    auto_speak_enabled: bool = Form(None),
    contact_email: str = Form(None),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Update bar settings
    Requires admin authentication
    """
    from backend.models.bar import BarSettings
    from datetime import datetime
    
    settings = db.query(BarSettings).first()
    if not settings:
        settings = BarSettings()
        db.add(settings)
    
    if llm_provider:
        settings.llm_provider = llm_provider
    if grok_api_key is not None:
        settings.grok_api_key = grok_api_key
    if ollama_model:
        settings.ollama_model = ollama_model
    if auto_speak_enabled is not None:
        settings.auto_speak_enabled = auto_speak_enabled
    if contact_email:
        settings.contact_email = contact_email
    
    settings.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(settings)
    
    return {"message": "Settings updated successfully", "settings": settings}


@router.post("/admin/menus/extract", summary="Extract text from menu file")
async def extract_menu_text(
    file: UploadFile = File(...),
    menu_type: str = Form(..., regex="^(daily|weekly)$"),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Upload menu file (PDF/JPG/PNG) and extract text content
    Uses LLM to extract and structure the menu text
    Requires admin authentication
    """
    try:
        # Read file content
        content = await file.read()

        # For images, use LLM vision to extract text
        # For now, use a simple approach: convert to base64 and use LLM
        if file.content_type in ['image/jpeg', 'image/png', 'image/jpg']:
            # Convert image to base64
            image_b64 = base64.b64encode(content).decode('utf-8')
            data_uri = f"data:{file.content_type};base64,{image_b64}"

            # Use LLM gateway to extract text from image
            from backend.services.llm_gateway import llm_gateway
            settings = db.query(BarSettings).first()

            prompt = f"""Extract all text content from this menu image.
Return the menu items with their descriptions and prices in a clean, structured format.
Format as a simple text list, one item per line."""

            result = llm_gateway.generate_with_image(
                prompt=prompt,
                image_data=data_uri,
                provider=settings.llm_provider if settings else "ollama",
                model=settings.ollama_model if settings else "llama3.2-vision"
            )
            extracted_text = result.get("text", "")

            return {
                "success": True,
                "extracted_text": extracted_text,
                "menu_type": menu_type
            }
        else:
            # For PDF, we'd need a PDF parser library
            # For now, return a placeholder
            raise HTTPException(
                status_code=400,
                detail="PDF extraction not yet implemented. Please use JPG or PNG images."
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract text: {str(e)}"
        )


@router.post("/admin/menus/translate", summary="Translate menu text")
async def translate_menu_text(
    text: str = Form(...),
    target_language: str = Form(..., regex="^(es|en|de|fr)$"),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Translate menu text to target language using LLM
    Requires admin authentication
    """
    try:
        # Use translation service to translate to ALL languages at once
        translations = await translation_service.translate_dish_name(
            db=db,
            dish_name=text,
            source_language="ca"  # Assume Catalan as source
        )

        # Return the specific target language
        translated_text = translations.get(target_language, text)

        return {
            "success": True,
            "translated_text": translated_text,
            "target_language": target_language
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/admin/menus", summary="Create menu with translations")
async def create_menu(
    menu_type: str = Form(..., regex="^(daily|weekly)$"),
    content_translations: str = Form(...),  # JSON string
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Create a new menu entry with translations
    Requires admin authentication
    """
    try:
        import json
        translations = json.loads(content_translations)

        menu = BarMenu(
            menu_type=menu_type,
            content_translations=translations,
            is_active=True,
            display_order=0
        )

        db.add(menu)
        db.commit()
        db.refresh(menu)

        # Index to Elasticsearch for RAG chatbot
        try:
            menu_dict = {
                "id": menu.id,
                "menu_type": menu.menu_type,
                "content_translations": menu.content_translations,
                "is_active": menu.is_active,
                "display_order": menu.display_order,
                "created_at": menu.created_at.isoformat() if menu.created_at else None
            }
            bar_es_service.index_menu(menu_dict)
        except Exception as es_error:
            # Log error but don't fail the entire request
            print(f"⚠️ Elasticsearch indexing failed (non-critical): {es_error}")

        return {
            "success": True,
            "message": "Menu created successfully",
            "menu": menu
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create menu: {str(e)}"
        )


# ==========================================
# FEATURED ITEMS MANAGEMENT
# ==========================================

@router.post("/admin/featured-items/translate", summary="Translate dish name to all languages")
async def translate_dish_name(
    dish_name: str = Form(...),
    source_language: str = Form(..., regex="^(ca|es|en|de|fr)$"),
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Translate a dish name from source language to all supported languages using LLM
    Requires admin authentication
    """
    try:
        translations = await LLMTranslationService.translate_dish_name(
            db, dish_name, source_language
        )
        return {
            "success": True,
            "translations": translations
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/admin/featured-items/upload-image", summary="Upload featured item image")
async def upload_featured_item_image(
    file: UploadFile = File(...),
    admin: str = Depends(verify_admin_token)
):
    """
    Upload an image for a featured item
    Requires admin authentication
    Returns the base64-encoded image as data URI
    """
    try:
        # Validate file type
        if not file.content_type in ['image/jpeg', 'image/png', 'image/jpg']:
            raise HTTPException(
                status_code=400,
                detail="Only JPG and PNG images are allowed"
            )

        # Read file content
        content = await file.read()

        # Convert to base64
        base64_data = base64.b64encode(content).decode('utf-8')

        # Determine MIME type
        mime_type = file.content_type

        # Create data URI
        data_uri = f"data:{mime_type};base64,{base64_data}"

        return {
            "success": True,
            "image_url": data_uri,
            "filename": file.filename,
            "size_kb": len(base64_data) / 1024
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image upload failed: {str(e)}"
        )


@router.put("/admin/featured-items/publish", summary="Publish featured items with translations")
async def publish_featured_items(
    featured_items: List[dict],
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Publish featured items to bar_info and index in Elasticsearch for RAG chat
    Each item should have: name (dict), description (dict), image (str)
    Requires admin authentication
    """
    try:
        # Update bar_info with new featured items
        bar_data = BarInfoUpdate(featured_items=featured_items)
        updated_bar = BarService.create_or_update_bar_info(db, bar_data)

        # Index in Elasticsearch for RAG chat
        try:
            es_service = BarElasticsearchService()
            # Convert SQLAlchemy model to dict for Elasticsearch
            bar_info_dict = {
                "description": updated_bar.description,
                "address": updated_bar.address,
                "phone": updated_bar.phone,
                "cuisine": updated_bar.cuisine,
                "price_range": updated_bar.price_range,
                "rating": updated_bar.rating,
                "location_lat": updated_bar.location_lat,
                "location_lng": updated_bar.location_lng,
                "opening_hours": updated_bar.opening_hours,
                "featured_items": updated_bar.featured_items
            }
            es_service.index_bar_info(bar_info_dict)
        except Exception as es_error:
            # Log error but don't fail the entire request
            print(f"⚠️ Elasticsearch indexing failed (non-critical): {es_error}")

        return {
            "success": True,
            "message": f"Published {len(featured_items)} featured items and indexed in Elasticsearch for chat",
            "featured_items": updated_bar.featured_items
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish featured items: {str(e)}"
        )


@router.get("/admin/newsletter/subscribers", summary="Get all newsletter subscribers")
async def get_newsletter_subscribers(
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Get all newsletter subscribers
    Requires admin authentication
    """
    try:
        subscribers = BarService.get_all_subscribers(db, active_only=False)
        return subscribers
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load subscribers: {str(e)}"
        )


@router.post("/admin/newsletter/send", summary="Send newsletter to all subscribers")
async def send_newsletter(
    newsletter_data: dict,
    db: Session = Depends(get_db),
    admin: str = Depends(verify_admin_token)
):
    """
    Send newsletter to all active subscribers
    newsletter_data should contain:
    - subject: dict with translations (ca, es, en, de, fr)
    - content: dict with translations (ca, es, en, de, fr)

    Requires admin authentication
    """
    try:
        # Get all active subscribers
        subscribers = BarService.get_all_subscribers(db, active_only=True)

        # Prepare subscriber data for batch sending
        subscriber_data = [
            (sub.email, sub.name, sub.language)
            for sub in subscribers
        ]

        # Send newsletter to all subscribers
        result = email_service.send_newsletter_batch(
            subscribers=subscriber_data,
            subject_translations=newsletter_data.get("subject", {}),
            content_translations=newsletter_data.get("content", {})
        )

        return {
            "success": True,
            "sent_count": result["success"],
            "failed_count": result["failed"],
            "total_count": result["total"],
            "message": f"Newsletter sent to {result['success']} of {result['total']} subscribers"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send newsletter: {str(e)}"
        )


# ========== TEAM ENDPOINTS ==========

@router.get("/team", response_model=List[BarTeamResponse], summary="Get published team members")
async def get_team_members(db: Session = Depends(get_db)):
    """Get all published team members - Public endpoint"""
    return BarTeamService.get_all_team_members(db, published_only=True)


@router.get("/admin/team", response_model=List[BarTeamResponse], summary="Get all team members")
async def admin_get_all_team_members(
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_token)
):
    """Get all team members (published and unpublished) - Admin only"""
    return BarTeamService.get_all_team_members(db, published_only=False)


@router.post("/admin/team", response_model=BarTeamResponse, status_code=status.HTTP_201_CREATED, summary="Create team member")
async def admin_create_team_member(
    team_data: BarTeamCreate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_token)
):
    """Create a new team member - Admin only"""
    # Check if we already have 5 team members
    existing_members = BarTeamService.get_all_team_members(db, published_only=False)
    if len(existing_members) >= 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum of 5 team members allowed"
        )
    team_member = BarTeamService.create_team_member(db, team_data)

    # Index in Elasticsearch if published
    if team_member.is_published:
        team_dict = {
            "id": team_member.id,
            "name": team_member.name,
            "description": team_member.description,
            "display_order": team_member.display_order,
            "is_published": team_member.is_published,
            "created_at": team_member.created_at.isoformat() if team_member.created_at else None
        }
        bar_es_service.index_team_member(team_dict)

    return team_member


@router.put("/admin/team/{team_id}", response_model=BarTeamResponse, summary="Update team member")
async def admin_update_team_member(
    team_id: int,
    team_data: BarTeamUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_token)
):
    """Update a team member - Admin only"""
    team_member = BarTeamService.update_team_member(db, team_id, team_data)
    if not team_member:
        raise HTTPException(status_code=404, detail="Team member not found")

    # Re-index in Elasticsearch
    team_dict = {
        "id": team_member.id,
        "name": team_member.name,
        "description": team_member.description,
        "display_order": team_member.display_order,
        "is_published": team_member.is_published,
        "created_at": team_member.created_at.isoformat() if team_member.created_at else None
    }
    bar_es_service.index_team_member(team_dict)

    return team_member


@router.delete("/admin/team/{team_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete team member")
async def admin_delete_team_member(
    team_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(verify_admin_token)
):
    """Delete a team member - Admin only"""
    success = BarTeamService.delete_team_member(db, team_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team member not found")

    # Delete from Elasticsearch
    bar_es_service.delete_team_member(team_id)

    return None
