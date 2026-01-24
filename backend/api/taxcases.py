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
from backend.services.application_service import DocumentParser

router = APIRouter()

# Simple in-memory auth storage (for MVP)
# In production, use proper JWT tokens and database storage
auth_tokens = {}
user_passwords = {}

# TEMPORARY: Fixed demo user UUID
DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

def get_demo_user(db: Session = Depends(get_db)) -> User:
    """Return demo user from DB"""
    user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    if not user:
        raise HTTPException(status_code=500, detail="Demo user not found - backend not initialized")
    return user


# Authentication Endpoints
@router.post("/auth/register", response_model=AuthResponse)
async def register_user(request: AuthRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user with email (password sent via email)"""
    # Check if user already exists
    if request.email in user_passwords:
        raise HTTPException(status_code=400, detail="Email already registered")

    # For MVP, store password in memory
    # In production, this would send email with password
    user_passwords[request.email] = "test123"

    # Generate simple token
    token = f"tax_token_{request.email}_{datetime.now().timestamp()}"
    auth_tokens[token] = request.email

    logger.info(f"User registered: {request.email} with password test123")

    return AuthResponse(
        token=token,
        email=request.email,
        message=f"Registration successful. Password 'test123' sent to {request.email}"
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login_user(request: AuthLoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    # Check credentials
    if request.email not in user_passwords:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user_passwords[request.email] != request.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate token
    token = f"tax_token_{request.email}_{datetime.now().timestamp()}"
    auth_tokens[token] = request.email

    logger.info(f"User logged in: {request.email}")

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
    db: Session = Depends(get_db),
    user: User = Depends(get_demo_user)
):
    """Upload and process documents for a tax case"""
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

    for file in files:
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Parse document content
        parser = DocumentParser()
        doc_content = parser.parse(file_path)

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

        # Extract data using LLM
        await extract_data_from_document(case.id, doc.id, doc_content, db)

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


async def extract_data_from_document(case_id: int, doc_id: int, content: str, db: Session):
    """Extract structured data from document using LLM"""
    from backend.services.llm_gateway import llm_gateway

    # Prepare extraction prompt
    prompt = f"""Extract the following information from this document:
- Name (name)
- Phone number (phone_number)
- Email (email)
- Address (address)
- Order positions (order_positions)
- Total amount (total_amount)
- Date (date)
- Any other relevant information

Document content:
{content[:4000]}

Return the extracted data as a JSON object with field names as keys.
"""

    try:
        # Use LLM to extract data
        result = await llm_gateway.generate(
            prompt=prompt,
            prefer_local=False  # Use Grok API for better accuracy
        )

        # Parse JSON response
        try:
            extracted = json.loads(result)
        except:
            # If not valid JSON, create structured response from text
            extracted = {"raw_text": result}

        # Store extracted data
        for field_name, field_value in extracted.items():
            if field_value:
                data_entry = TaxCaseExtractedData(
                    tax_case_id=case_id,
                    document_id=doc_id,
                    field_name=field_name,
                    field_value=str(field_value),
                    field_type="text",
                    confidence=0.8,
                    confirmed=False
                )
                db.add(data_entry)

        db.flush()
        logger.info(f"Extracted {len(extracted)} fields from document {doc_id}")

    except Exception as e:
        logger.error(f"Error extracting data: {e}")


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
