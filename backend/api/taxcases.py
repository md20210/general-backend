"""Tax Case Management API Endpoints"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import os
import logging
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

logger = logging.getLogger(__name__)

from backend.database import get_db
from backend.models.taxcase import TaxCase, TaxCaseDocument, TaxCaseFolder, TaxCaseExtractedData
from backend.models.user import User
from backend.schemas.taxcase import (
    TaxCaseCreate, TaxCaseResponse, TaxCaseDetailResponse,
    DocumentResponse, ExtractedDataResponse, ExtractedDataBulkUpdate,
    AuthRegisterRequest, AuthLoginRequest, AuthResponse
)
try:
    from backend.services.application_service import DocumentParser
except ImportError:
    DocumentParser = None

router = APIRouter()

# TEMPORARY: Fixed demo user UUID (same as applications)
DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

def get_demo_user(db: Session = Depends(get_db)) -> User:
    """Return demo user from DB"""
    user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    if not user:
        raise HTTPException(status_code=500, detail="Demo user not found - backend not initialized")
    return user


# Authentication Endpoints (Simplified for MVP - just return token)
@router.post("/auth/register", response_model=AuthResponse)
async def register_user(request: AuthRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email (password sent via email)"""
    # For MVP: Just accept any email and return success
    token = f"tax_demo_token_{datetime.now().timestamp()}"

    logger.info(f"User registered (MVP mode): {request.email}")

    return AuthResponse(
        token=token,
        email=request.email,
        message=f"Registration successful. Password 'test123' sent to {request.email}"
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login_user(request: AuthLoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    # For MVP: Accept any email with password "test123"
    if request.password != "test123":
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = f"tax_demo_token_{datetime.now().timestamp()}"

    logger.info(f"User logged in (MVP mode): {request.email}")

    return AuthResponse(
        token=token,
        email=request.email,
        message="Login successful"
    )


# Tax Case Endpoints
@router.get("/cases", response_model=List[TaxCaseResponse])
async def list_tax_cases(db: Session = Depends(get_db), user: User = Depends(get_demo_user)):
    """List all tax cases for the authenticated user"""
    cases = db.query(TaxCase).filter(TaxCase.user_id == user.id).order_by(desc(TaxCase.created_at)).all()

    response = []
    for case in cases:
        doc_count = db.query(func.count(TaxCaseDocument.id)).filter(
            TaxCaseDocument.tax_case_id == case.id
        ).scalar()

        response.append(TaxCaseResponse(
            id=case.id,
            name=case.name,
            status=case.status,
            validated=case.validated,
            document_count=doc_count or 0,
            created_at=case.created_at
        ))

    return response


@router.post("/cases", response_model=TaxCaseResponse)
async def create_tax_case(
    case_data: TaxCaseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user)
):
    """Create a new tax case"""
    new_case = TaxCase(
        user_id=user.id,
        name=case_data.name,
        notes=case_data.notes,
        status="created"
    )

    db.add(new_case)
    db.commit()
    db.refresh(new_case)

    logger.info(f"Created tax case: {new_case.id} - {new_case.name}")

    return TaxCaseResponse(
        id=new_case.id,
        name=new_case.name,
        status=new_case.status,
        validated=new_case.validated,
        document_count=0,
        created_at=new_case.created_at
    )


@router.get("/cases/{case_id}", response_model=TaxCaseDetailResponse)
async def get_tax_case(case_id: int, db: Session = Depends(get_db), user: User = Depends(get_demo_user)):
    """Get detailed information about a tax case"""
    case = db.query(TaxCase).filter(
        TaxCase.id == case_id,
        TaxCase.user_id == user.id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Tax case not found")

    # Get document count
    doc_count = db.query(func.count(TaxCaseDocument.id)).filter(
        TaxCaseDocument.tax_case_id == case.id
    ).scalar()

    # Get extracted data as dictionary
    extracted_items = db.query(TaxCaseExtractedData).filter(
        TaxCaseExtractedData.tax_case_id == case.id
    ).all()

    extracted_data = {}
    for item in extracted_items:
        extracted_data[item.field_name] = item.field_value

    return TaxCaseDetailResponse(
        id=case.id,
        name=case.name,
        status=case.status,
        validated=case.validated,
        notes=case.notes,
        document_count=doc_count or 0,
        extracted_data=extracted_data,
        created_at=case.created_at,
        updated_at=case.updated_at
    )


@router.post("/cases/{case_id}/upload")
async def upload_documents(
    case_id: int,
    files: List[UploadFile] = File(...),
    use_local_llm: str = Form("true"),  # DSGVO mode by default
    ocr_engine: str = Form("tesseract"),
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user)
):
    """Upload and process documents for a tax case"""
    prefer_local = use_local_llm.lower() == "true"
    ocr_mode = "PaddleOCR" if ocr_engine.lower() == "paddle" else "Tesseract OCR"
    logger.info(f"Upload mode: {'DSGVO (lokales LLM)' if prefer_local else 'Grok API'} mit {ocr_mode}")
    case = db.query(TaxCase).filter(
        TaxCase.id == case_id,
        TaxCase.user_id == user.id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Tax case not found")

    # Create uploads directory if it doesn't exist
    upload_dir = f"/tmp/tax_uploads/{case_id}"
    os.makedirs(upload_dir, exist_ok=True)

    uploaded_docs = []

    try:
        for file in files:
            # Save file
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # For MVP: Just extract text from PDF or use placeholder
            doc_content = f"Document content from {file.filename}"

            # Try to parse with DocumentParser if available
            if DocumentParser:
                try:
                    parser = DocumentParser()
                    doc_content = parser.parse(file_path, ocr_engine=ocr_engine.lower())
                    logger.info(f"{ocr_mode} extracted text from {file.filename}")
                except Exception as parse_error:
                    logger.warning(f"{ocr_mode} could not parse document {file.filename}: {parse_error}")
                    # Use basic content
                    doc_content = f"Uploaded: {file.filename} ({ocr_mode} nicht verfügbar)"
            else:
                doc_content = f"Uploaded: {file.filename}"

            # Create document record
            doc = TaxCaseDocument(
                tax_case_id=case.id,
                filename=file.filename,
                file_path=file_path,
                doc_type="document",
                content=doc_content,
                validated=False
            )

            db.add(doc)
            db.flush()

            # Extract data using LLM (always creates data, even if LLM fails)
            await extract_data_from_document(case.id, doc.id, doc_content, db, prefer_local)

            uploaded_docs.append(doc.id)

        # Update case status
        case.status = "processing"
        db.commit()

        logger.info(f"Uploaded {len(files)} documents to case {case_id}")

        return {
            "success": True,
            "message": f"{len(files)} documents uploaded and processed",
            "document_ids": uploaded_docs
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


async def extract_data_from_document(case_id: int, doc_id: int, content: str, db: Session, prefer_local: bool = True):
    """Extract structured data from document using LLM"""

    # For MVP: Create sample extracted data
    llm_mode = "Lokales LLM (DSGVO)" if prefer_local else "Grok API"
    sample_data = {
        "document_content": content[:200] if content else "No content",
        "status": "Hochgeladen und bereit zur Verarbeitung",
        "verarbeitungsmodus": llm_mode,
        "hinweis": "Bitte bearbeiten Sie diese Felder und bestätigen Sie den Fall"
    }

    # Try to use LLM if available
    try:
        from backend.services.llm_gateway import llm_gateway

        # Prepare extraction prompt (H7-Formular für Kanarische Inseln)
        prompt = f"""Extrahiere folgende Informationen aus diesem Dokument für Import auf die Kanarischen Inseln:

1. SENDUNGSDATEN: art_der_sendung, warenwert_gesamt_eur, versandkosten, art_der_lieferung
2. ABSENDER: absender_name, absender_strasse, absender_plz, absender_ort, absender_land, absender_email, absender_telefon
3. EMPFÄNGER: empfaenger_name, empfaenger_strasse, empfaenger_plz, empfaenger_ort, empfaenger_insel, empfaenger_nif_nie_cif, empfaenger_email, empfaenger_telefon
4. WARENPOSITION: position_1_beschreibung, position_1_anzahl, position_1_stueckpreis, position_1_gesamtwert, position_1_ursprungsland
5. RECHNUNG: rechnungsnummer, rechnungsdatum, mehrwertsteuer_ausgewiesen

Dokumenteninhalt:
{content[:4000]}

Gib die Daten als JSON zurück. Verwende exakt die angegebenen Feldnamen.
Falls Felder nicht gefunden werden, lass sie weg.
"""

        # Use LLM to extract data with DSGVO preference
        provider = "ollama" if prefer_local else "grok"
        timeout = 120 if provider == "ollama" else 60  # 120 seconds for Ollama, 60 seconds for Grok
        result_dict = llm_gateway.generate(
            prompt=prompt,
            provider=provider,
            max_tokens=3000,
            timeout=timeout
        )
        result = result_dict.get("response", "")

        logger.info(f"LLM extraction mode: {llm_mode} using {provider}")

        # Parse JSON response
        try:
            extracted = json.loads(result)
            # Merge with sample data
            sample_data.update(extracted)
        except:
            # If not valid JSON, just use sample data
            sample_data["llm_response"] = result[:200]

        logger.info(f"LLM extraction successful for document {doc_id}")

    except Exception as e:
        logger.warning(f"LLM extraction failed for document {doc_id}: {e}")
        # Continue with sample data

    # Store extracted data (either from LLM or sample)
    for field_name, field_value in sample_data.items():
        if field_value:
            data_entry = TaxCaseExtractedData(
                tax_case_id=case_id,
                document_id=doc_id,
                field_name=field_name,
                field_value=str(field_value),
                field_type="text",
                confidence=0.5,
                confirmed=False
            )
            db.add(data_entry)

    db.flush()
    logger.info(f"Stored {len(sample_data)} fields for document {doc_id}")


@router.get("/cases/{case_id}/documents", response_model=List[DocumentResponse])
async def list_documents(case_id: int, db: Session = Depends(get_db), user: User = Depends(get_demo_user)):
    """List all documents for a tax case"""
    case = db.query(TaxCase).filter(
        TaxCase.id == case_id,
        TaxCase.user_id == user.id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Tax case not found")

    documents = db.query(TaxCaseDocument).filter(
        TaxCaseDocument.tax_case_id == case_id
    ).order_by(desc(TaxCaseDocument.created_at)).all()

    return [DocumentResponse(
        id=doc.id,
        tax_case_id=doc.tax_case_id,
        folder_id=doc.folder_id,
        filename=doc.filename,
        doc_type=doc.doc_type or "document",
        validated=doc.validated,
        created_at=doc.created_at
    ) for doc in documents]


@router.put("/cases/{case_id}/data")
async def update_extracted_data(
    case_id: int,
    data_update: ExtractedDataBulkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user)
):
    """Update extracted data for a tax case"""
    case = db.query(TaxCase).filter(
        TaxCase.id == case_id,
        TaxCase.user_id == user.id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Tax case not found")

    # Update each field
    for field_name, field_value in data_update.data.items():
        existing = db.query(TaxCaseExtractedData).filter(
            TaxCaseExtractedData.tax_case_id == case_id,
            TaxCaseExtractedData.field_name == field_name
        ).first()

        if existing:
            if existing.field_value != str(field_value):
                existing.original_value = existing.field_value
                existing.field_value = str(field_value)
                existing.edited = True
        else:
            # Create new field
            new_data = TaxCaseExtractedData(
                tax_case_id=case_id,
                field_name=field_name,
                field_value=str(field_value),
                field_type="text",
                edited=True
            )
            db.add(new_data)

    db.commit()
    logger.info(f"Updated extracted data for case {case_id}")

    return {"success": True, "message": "Data updated successfully"}


@router.post("/cases/{case_id}/confirm")
async def confirm_case(case_id: int, db: Session = Depends(get_db), user: User = Depends(get_demo_user)):
    """Confirm and validate a tax case after review"""
    case = db.query(TaxCase).filter(
        TaxCase.id == case_id,
        TaxCase.user_id == user.id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Tax case not found")

    # Mark case as validated
    case.validated = True
    case.status = "confirmed"

    # Mark all extracted data as confirmed
    db.query(TaxCaseExtractedData).filter(
        TaxCaseExtractedData.tax_case_id == case_id
    ).update({"confirmed": True})

    # Mark all documents as validated
    db.query(TaxCaseDocument).filter(
        TaxCaseDocument.tax_case_id == case_id
    ).update({"validated": True})

    db.commit()
    logger.info(f"Confirmed tax case {case_id}")

    return {"success": True, "message": "Case confirmed successfully"}


@router.get("/cases/{case_id}/export")
async def export_case_pdf(case_id: int, db: Session = Depends(get_db), user: User = Depends(get_demo_user)):
    """Export tax case data to PDF"""
    case = db.query(TaxCase).filter(
        TaxCase.id == case_id,
        TaxCase.user_id == user.id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Tax case not found")

    # Get extracted data
    extracted_items = db.query(TaxCaseExtractedData).filter(
        TaxCaseExtractedData.tax_case_id == case_id
    ).all()

    # Create PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Steuerfall: {case.name}")

    # Metadata
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 80, f"Status: {case.status}")
    p.drawString(50, height - 95, f"Erstellt: {case.created_at.strftime('%d.%m.%Y %H:%M')}")
    p.drawString(50, height - 110, f"Validiert: {'Ja' if case.validated else 'Nein'}")

    # Extracted Data
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 140, "Extrahierte Daten:")

    p.setFont("Helvetica", 10)
    y_position = height - 160
    for item in extracted_items:
        if y_position < 50:
            p.showPage()
            y_position = height - 50

        p.drawString(50, y_position, f"{item.field_name}: {item.field_value}")
        y_position -= 15

    p.showPage()
    p.save()

    buffer.seek(0)
    logger.info(f"Exported PDF for case {case_id}")

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=fall_{case_id}_export.pdf"}
    )


@router.get("/documents/{doc_id}/download")
async def download_document(doc_id: int, db: Session = Depends(get_db), user: User = Depends(get_demo_user)):
    """Download a specific document"""
    doc = db.query(TaxCaseDocument).filter(TaxCaseDocument.id == doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Verify ownership
    case = db.query(TaxCase).filter(
        TaxCase.id == doc.tax_case_id,
        TaxCase.user_id == user.id
    ).first()

    if not case:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check if file exists
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    def file_iterator():
        with open(doc.file_path, "rb") as f:
            yield from f

    return StreamingResponse(
        file_iterator(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={doc.filename}"}
    )


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "taxcases", "version": "1.0.0"}


# Debug endpoint
@router.get("/debug/check-services")
async def debug_check_services():
    """Debug: Check OCR and LLM services availability"""
    status = {
        "tesseract": False,
        "paddleocr": False,
        "ollama": False,
        "grok": False,
        "errors": {}
    }

    # Check Tesseract
    try:
        from PIL import Image
        import pytesseract
        status["tesseract"] = True
    except Exception as e:
        status["errors"]["tesseract"] = str(e)

    # Check PaddleOCR
    try:
        from backend.services.application_service import get_paddle_ocr, PADDLE_AVAILABLE
        if PADDLE_AVAILABLE:
            ocr = get_paddle_ocr()
            if ocr:
                status["paddleocr"] = True
                status["paddleocr_version"] = "3.3.3 with latin language"
            else:
                status["paddleocr"] = False
                status["errors"]["paddleocr"] = "Initialization failed"
        else:
            status["paddleocr"] = False
            status["errors"]["paddleocr"] = "PaddleOCR not installed"
    except Exception as e:
        status["errors"]["paddleocr"] = str(e)

    # Check Ollama
    try:
        from backend.services.llm_gateway import llm_gateway
        result = llm_gateway.generate(prompt="Test", provider="ollama", max_tokens=10, timeout=10)
        status["ollama"] = True
        status["ollama_response"] = result.get("response", "")[:50]
    except Exception as e:
        status["errors"]["ollama"] = str(e)

    # Check Grok
    try:
        from backend.services.llm_gateway import llm_gateway
        from backend.config import settings
        if settings.GROK_API_KEY and settings.GROK_API_KEY.strip():
            status["grok"] = "API key configured"
        else:
            status["grok"] = False
            status["errors"]["grok"] = "API key not configured"
    except Exception as e:
        status["errors"]["grok"] = str(e)

    return status


# FREE TAB ENDPOINTS
@router.post("/free/upload")
async def free_upload(
    email: str = Form(...),
    files: List[UploadFile] = File(...),
    use_local_llm: str = Form("true"),
    ocr_engine: str = Form("tesseract"),
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user)
):
    """Free tier: Upload documents and extract data - SAVES to database"""
    prefer_local = use_local_llm.lower() == "true"
    llm_mode = "Lokales LLM (DSGVO)" if prefer_local else "Grok API"
    ocr_mode = "PaddleOCR" if ocr_engine.lower() == "paddle" else "Tesseract OCR"

    # Create a case for this upload (so it appears in Premium tab)
    from datetime import datetime
    case_name = f"Free Upload - {email} - {datetime.now().strftime('%d.%m.%Y %H:%M')}"

    new_case = TaxCase(
        user_id=user.id,
        name=case_name,
        status="processing",
        notes=f"Erstellt über Free Tab mit {llm_mode} und {ocr_mode}"
    )
    db.add(new_case)
    db.flush()

    case_id = new_case.id
    logger.info(f"Created case {case_id} for free upload from {email} using {ocr_mode}")

    # Create upload directory
    upload_dir = f"/tmp/tax_uploads/{case_id}"
    os.makedirs(upload_dir, exist_ok=True)

    extracted_data = {
        "verarbeitungsmodus": llm_mode,
        "ocr_engine": ocr_mode,
        "email": email
    }

    try:
        all_content = []

        for file in files:
            # Save file
            file_path = os.path.join(upload_dir, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # Extract text with OCR/DocumentParser
            doc_content = ""
            if DocumentParser:
                try:
                    parser = DocumentParser()
                    doc_content = parser.parse(file_path, ocr_engine=ocr_engine.lower())
                    logger.info(f"{ocr_mode} extracted {len(doc_content)} characters from {file.filename}")
                except Exception as parse_error:
                    logger.warning(f"{ocr_mode} failed for {file.filename}: {parse_error}")
                    doc_content = f"Dokument: {file.filename} (OCR nicht verfügbar: {str(parse_error)})"
            else:
                doc_content = f"Dokument: {file.filename}"

            # Save document to database
            doc = TaxCaseDocument(
                tax_case_id=case_id,
                filename=file.filename,
                file_path=file_path,
                doc_type="document",
                content=doc_content,
                validated=False
            )
            db.add(doc)
            db.flush()

            all_content.append(f"--- {file.filename} ---\n{doc_content}\n")

        # Combine all document content
        combined_content = "\n\n".join(all_content)

        # Extract with LLM
        try:
            from backend.services.llm_gateway import llm_gateway

            prompt = f"""Extrahiere folgende Informationen aus diesem Dokument für Import auf die Kanarischen Inseln (H7-Formular):

1. ALLGEMEINE SENDUNGSDATEN:
- art_der_sendung: B2C (Business to Consumer) oder C2C (Consumer to Consumer)
- warenwert_gesamt_eur: Gesamtwert der Waren in EUR
- waehrung: Währung (meist EUR)
- versandkosten: Versandkosten
- versicherungskosten: Versicherungskosten (optional)
- gesamtbetrag_fuer_zoll: Summe aus Wert + Versand + Versicherung
- art_der_lieferung: Kauf oder Geschenk

2. ABSENDER (Versender):
- absender_name: Name oder Firma des Absenders
- absender_strasse: Straße und Hausnummer
- absender_plz: Postleitzahl
- absender_ort: Ort
- absender_land: Land (ISO-Code)
- absender_email: E-Mail (optional)
- absender_telefon: Telefonnummer (optional)

3. EMPFÄNGER (Kanarische Inseln):
- empfaenger_name: Name des Empfängers
- empfaenger_strasse: Straße und Hausnummer
- empfaenger_plz: Postleitzahl
- empfaenger_ort: Ort
- empfaenger_insel: Welche kanarische Insel (wichtig!)
- empfaenger_nif_nie_cif: NIF/NIE/CIF Nummer (sehr wichtig!)
- empfaenger_email: E-Mail
- empfaenger_telefon: Telefonnummer

4. WARENPOSITIONEN (mindestens 1):
- position_1_beschreibung: Klare Warenbeschreibung
- position_1_anzahl: Stückzahl
- position_1_stueckpreis: Preis pro Stück
- position_1_gesamtwert: Gesamtwert der Position
- position_1_ursprungsland: Ursprungsland (ISO-Code)
- position_1_zolltarifnummer: 6-stellige Zolltarifnummer (optional)
- position_1_gewicht: Gewicht (optional)
- position_1_zustand: Neu oder gebraucht (optional)

5. RECHNUNGS-/WERTNACHWEIS:
- rechnungsnummer: Nummer der Rechnung
- rechnungsdatum: Datum der Rechnung
- mehrwertsteuer_ausgewiesen: Ja/Nein, wurde MwSt ausgewiesen?

6. ZUSÄTZLICHE ANGABEN:
- zahlungsnachweis: Art des Zahlungsnachweises (PayPal, Karte, etc.)
- bemerkungen: Weitere Anmerkungen

Dokumenteninhalt:
{combined_content[:8000]}

Gib die extrahierten Daten als JSON-Objekt zurück.
Verwende exakt die Feldnamen wie oben angegeben.
Falls ein Feld nicht gefunden wird, lasse es weg oder gib null zurück.
Bei mehreren Warenpositionen verwende position_2_*, position_3_* usw.
"""

            # Convert prefer_local to provider
            provider = "ollama" if prefer_local else "grok"
            # Ollama on Railway is CPU-only and slow, needs longer timeout
            timeout = 120 if provider == "ollama" else 60  # 120 seconds for Ollama, 60 seconds for Grok
            result_dict = llm_gateway.generate(prompt=prompt, provider=provider, max_tokens=4000, timeout=timeout)
            result = result_dict.get("response", "")

            logger.info(f"LLM extraction completed with {llm_mode} using {provider}")

            # Parse LLM response
            try:
                llm_data = json.loads(result)
                extracted_data.update(llm_data)
                logger.info(f"Successfully parsed {len(llm_data)} fields from LLM response")
            except json.JSONDecodeError:
                # If not valid JSON, try to extract key info from text
                logger.warning("LLM response is not valid JSON, using fallback")
                extracted_data["llm_antwort"] = result[:1000]
                # Add some basic extracted info
                extracted_data["inhalt_vorschau"] = combined_content[:500]

        except Exception as llm_error:
            logger.error(f"LLM extraction failed: {llm_error}")
            # Fallback: provide document preview
            extracted_data["fehler"] = "LLM-Extraktion fehlgeschlagen"
            extracted_data["dokument_vorschau"] = combined_content[:800]
            extracted_data["hinweis"] = "Bitte überprüfen und manuell ausfüllen"

        # Ensure we have some data
        if len(extracted_data) <= 2:  # Only mode and email
            extracted_data["status"] = "Dokumente hochgeladen"
            extracted_data["dokument_inhalt"] = combined_content[:500]
            extracted_data["hinweis"] = "Bitte Daten manuell überprüfen und ergänzen"

        # Save extracted data to database
        for field_name, field_value in extracted_data.items():
            if field_value:
                data_entry = TaxCaseExtractedData(
                    tax_case_id=case_id,
                    field_name=field_name,
                    field_value=str(field_value),
                    field_type="text",
                    confidence=0.7,
                    confirmed=False
                )
                db.add(data_entry)

        # Mark case as validated
        new_case.status = "validated"
        db.commit()

        logger.info(f"Saved case {case_id} with {len(extracted_data)} extracted fields to database")

        return {
            "success": True,
            "extracted_data": extracted_data,
            "case_id": case_id,
            "message": f"Dokumente erfolgreich verarbeitet und gespeichert ({llm_mode})"
        }

    except Exception as e:
        logger.error(f"Error in free upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/free/create-document")
async def free_create_document(
    data: dict,
    db: Session = Depends(get_db)
):
    """Free tier: Create PDF document from extracted data"""
    try:
        email = data.get("email", "unknown@email.com")
        extracted_data = data.get("data", {})

        # Create PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Title
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, height - 50, "Steuerdokument - Tax Document")

        # Email and date
        p.setFont("Helvetica", 10)
        p.drawString(50, height - 80, f"Erstellt für / Created for: {email}")
        p.drawString(50, height - 95, f"Datum / Date: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

        # Separator line
        p.line(50, height - 105, width - 50, height - 105)

        # Data section
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, height - 130, "Extrahierte Daten / Extracted Data:")

        p.setFont("Helvetica", 10)
        y_position = height - 155

        # Sort data to show important fields first
        priority_fields = ["name", "adresse", "steuernummer", "gesamtbetrag", "datum", "email", "telefon"]
        sorted_data = {}

        # Add priority fields first
        for field in priority_fields:
            if field in extracted_data:
                sorted_data[field] = extracted_data[field]

        # Add remaining fields
        for key, value in extracted_data.items():
            if key not in priority_fields:
                sorted_data[key] = value

        # Render data
        for key, value in sorted_data.items():
            if y_position < 50:
                p.showPage()
                p.setFont("Helvetica", 10)
                y_position = height - 50

            # Format key nicely
            key_formatted = key.replace("_", " ").title()

            # Handle long values
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."

            p.setFont("Helvetica-Bold", 10)
            p.drawString(50, y_position, f"{key_formatted}:")
            p.setFont("Helvetica", 10)
            p.drawString(200, y_position, value_str)

            y_position -= 20

        # Footer
        p.line(50, 50, width - 50, 50)
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, 35, "Dieses Dokument wurde automatisch erstellt. Bitte überprüfen Sie alle Angaben.")
        p.drawString(50, 25, "This document was automatically created. Please verify all information.")

        p.showPage()
        p.save()

        buffer.seek(0)

        logger.info(f"PDF created for {email} with {len(sorted_data)} fields")

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=steuerdokument_{email.split('@')[0]}.pdf"}
        )
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ADMIN TAB ENDPOINTS
@router.get("/admin/users")
async def get_all_users(db: Session = Depends(get_db), user: User = Depends(get_demo_user)):
    """Admin: Get all users with their cases"""
    # For MVP: Return demo data structure
    # In production: Query actual users

    cases = db.query(TaxCase).all()

    # Group by user email (for MVP, all belong to demo user)
    user_data = {
        "demo@example.com": {
            "email": "demo@example.com",
            "folders": [],
            "case_count": len(cases)
        }
    }

    return list(user_data.values())


# CASE MANAGEMENT ENDPOINTS
class CaseUpdateRequest(BaseModel):
    name: Optional[str] = None
    notes: Optional[str] = None

@router.put("/cases/{case_id}")
async def update_case(
    case_id: int,
    update_data: CaseUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user)
):
    """Update case (rename, edit notes)"""
    case = db.query(TaxCase).filter(
        TaxCase.id == case_id,
        TaxCase.user_id == user.id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if update_data.name:
        case.name = update_data.name
    if update_data.notes is not None:
        case.notes = update_data.notes

    db.commit()
    db.refresh(case)

    logger.info(f"Updated case {case_id}: name={update_data.name}")

    return {"success": True, "message": "Case updated"}


@router.delete("/cases/{case_id}")
async def delete_case(
    case_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user)
):
    """Delete a case and all associated data"""
    case = db.query(TaxCase).filter(
        TaxCase.id == case_id,
        TaxCase.user_id == user.id
    ).first()

    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Delete case (cascade will delete documents and extracted data)
    db.delete(case)
    db.commit()

    logger.info(f"Deleted case {case_id}")

    return {"success": True, "message": "Case deleted"}
