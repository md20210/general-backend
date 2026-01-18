"""Application Tracker API Endpoints

⚠️  TEMPORARY TESTING MODE - NO AUTH ⚠️
All endpoints use a fixed demo UUID for testing.
TODO: Re-enable authentication before production!
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import re
import logging

logger = logging.getLogger(__name__)

from backend.database import get_db
from backend.models.application import (
    Application,
    ApplicationDocument,
    ApplicationFolder,
    ApplicationStatusHistory,
    ApplicationChatMessage
)
from backend.models.user import User
from backend.schemas.application import (
    ApplicationResponse,
    ApplicationDetailResponse,
    StatusUpdateRequest,
    ChatMessageRequest,
    ChatMessageResponse,
    GenerateReportRequest,
    ReportResponse,
    RenameApplicationRequest,
    MoveDocumentRequest,
    FolderResponse,
    CreateFolderRequest,
    RenameFolderRequest,
    MoveFolderRequest
)
from backend.services.application_service import DocumentParser, guess_doc_type, classify_document_with_llm, extract_application_info
from backend.services.vector_service import VectorService
from backend.services.llm_gateway import llm_gateway
from backend.services.application_elasticsearch_service import application_es_service

router = APIRouter()

# TEMPORARY: Fixed demo user UUID (no auth needed)
DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")

def get_demo_user(db: Session = Depends(get_db)) -> User:
    """TEMPORARY: Return real demo user from DB without any auth check"""
    user = db.query(User).filter(User.id == DEMO_USER_ID).first()
    if not user:
        raise HTTPException(status_code=500, detail="Demo user not found - backend not initialized")
    return user


# TEMPORARY TEST ENDPOINTS - NO AUTH, NO USER
@router.get("/test/ping")
async def test_ping():
    """Test endpoint - no auth required"""
    return {"status": "ok", "message": "Application Tracker is alive", "version": "2026-01-18-fix4-text"}


@router.get("/test/add-indexed-column")
async def add_indexed_column(db: Session = Depends(get_db)):
    """Manually add indexed column if it doesn't exist"""
    try:
        # Try to add the column
        db.execute(text("ALTER TABLE application_documents ADD COLUMN indexed BOOLEAN NOT NULL DEFAULT false"))
        db.execute(text("CREATE INDEX ix_application_documents_indexed ON application_documents (indexed)"))
        db.commit()
        return {
            "success": True,
            "message": "Added indexed column successfully"
        }
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            return {
                "success": True,
                "message": "Column already exists"
            }
        return {
            "success": False,
            "error": error_msg
        }


@router.get("/test/add-folder-hierarchy")
async def add_folder_hierarchy(db: Session = Depends(get_db)):
    """Manually create application_folders table and add folder_id to documents"""
    try:
        # Create application_folders table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS application_folders (
                id SERIAL PRIMARY KEY,
                application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                parent_id INTEGER REFERENCES application_folders(id) ON DELETE CASCADE,
                path VARCHAR(2000) NOT NULL,
                level INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Add indexes
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_application_folders_application_id ON application_folders (application_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_application_folders_parent_id ON application_folders (parent_id)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_application_folders_path ON application_folders (path)"))

        # Add folder_id column to application_documents
        db.execute(text("ALTER TABLE application_documents ADD COLUMN IF NOT EXISTS folder_id INTEGER REFERENCES application_folders(id) ON DELETE CASCADE"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_application_documents_folder_id ON application_documents (folder_id)"))

        db.commit()
        return {
            "success": True,
            "message": "Added folder hierarchy successfully"
        }
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        return {
            "success": False,
            "error": error_msg
        }


@router.get("/test/elasticsearch-status")
async def test_elasticsearch_status():
    """Check Elasticsearch connection status"""
    es_connected = application_es_service.es is not None
    es_ping = False

    if es_connected:
        try:
            es_ping = application_es_service.es.ping()
        except:
            pass

    return {
        "elasticsearch_connected": es_connected,
        "elasticsearch_ping": es_ping,
        "index_name": application_es_service.index_name,
        "message": "Elasticsearch is running" if (es_connected and es_ping) else "Elasticsearch not available (using PostgreSQL pgvector only)"
    }


@router.post("/test/create-demo-user")
async def create_demo_user_endpoint(db: Session = Depends(get_db)):
    """Manually create demo user for testing"""
    try:
        # Check if exists
        existing_user = db.query(User).filter(User.id == DEMO_USER_ID).first()

        if existing_user:
            return {"status": "exists", "message": "Demo user already exists", "id": str(existing_user.id)}

        # Create demo user using User model
        demo_user = User(
            id=DEMO_USER_ID,
            email="demo@applicationtracker.test",
            hashed_password="$2b$12$dummyhashfordemouseronly0000000000000000000000000",  # dummy hash
            is_active=True,
            is_superuser=False,
            is_verified=True,
            is_admin=False
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

        return {"status": "created", "message": "Demo user created successfully", "id": str(demo_user.id)}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


@router.get("/test/overview")
async def test_overview(db: Session = Depends(get_db)):
    """Test overview - returns ALL applications (no user filter)"""
    applications = db.query(Application).all()
    return {
        "count": len(applications),
        "applications": [{
            "id": app.id,
            "company_name": app.company_name,
            "position": app.position,
            "status": app.status
        } for app in applications[:10]]  # First 10
    }


@router.get("/overview", response_model=List[ApplicationResponse])
async def get_applications_overview(
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Get overview of all applications with document breakdown"""
    applications = db.query(Application).filter(Application.user_id == user.id).all()

    result = []
    for app in applications:
        # Get all documents for this application
        documents = db.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == app.id
        ).all()

        # Categorize documents by type
        cv_file = None
        cv_document_id = None
        cover_letter_file = None
        cover_letter_document_id = None
        job_description_file = None
        job_description_document_id = None
        other_files = []

        for doc in documents:
            # Check each type independently (not elif chain)
            if doc.doc_type == 'cv' and not cv_file:
                cv_file = doc.filename
                cv_document_id = doc.id
            if doc.doc_type == 'cover_letter' and not cover_letter_file:
                cover_letter_file = doc.filename
                cover_letter_document_id = doc.id
            if doc.doc_type == 'job_description' and not job_description_file:
                job_description_file = doc.filename
                job_description_document_id = doc.id
            # Only count as "other" if it's not one of the main types
            if doc.doc_type not in ['cv', 'cover_letter', 'job_description']:
                other_files.append(doc.filename)

        result.append(ApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            company_name=app.company_name,
            position=app.position,
            status=app.status,
            notes=app.notes,
            upload_path=app.upload_path,
            created_at=app.created_at,
            updated_at=app.updated_at,
            document_count=len(documents),
            cv_file=cv_file,
            cv_document_id=cv_document_id,
            cover_letter_file=cover_letter_file,
            cover_letter_document_id=cover_letter_document_id,
            job_description_file=job_description_file,
            job_description_document_id=job_description_document_id,
            other_files_count=len(other_files)
        ))

    return result


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
async def get_application_detail(
    application_id: int,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Get detailed application info with documents and status history"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    documents = db.query(ApplicationDocument).filter(
        ApplicationDocument.application_id == application_id
    ).all()

    history = db.query(ApplicationStatusHistory).filter(
        ApplicationStatusHistory.application_id == application_id
    ).order_by(ApplicationStatusHistory.changed_at.desc()).all()

    return ApplicationDetailResponse(
        id=app.id,
        user_id=app.user_id,
        company_name=app.company_name,
        position=app.position,
        status=app.status,
        notes=app.notes,
        upload_path=app.upload_path,
        created_at=app.created_at,
        updated_at=app.updated_at,
        document_count=len(documents),
        documents=documents,
        status_history=history
    )


@router.patch("/{application_id}/status")
async def update_application_status(
    application_id: int,
    status_update: StatusUpdateRequest,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Update application status and log to history"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    history_entry = ApplicationStatusHistory(
        application_id=application_id,
        old_status=app.status,
        new_status=status_update.status,
        notes=status_update.notes
    )
    db.add(history_entry)

    app.status = status_update.status
    app.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "application_id": application_id,
        "old_status": history_entry.old_status,
        "new_status": history_entry.new_status
    }


@router.delete("/test/delete-all")
async def delete_all_applications(
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """TESTING ONLY: Delete ALL applications for demo user"""
    try:
        # Delete documents first to avoid cascade issues
        db.execute(text("DELETE FROM application_documents WHERE application_id IN (SELECT id FROM applications WHERE user_id = :user_id)"), {"user_id": str(user.id)})

        # Delete applications
        deleted_count = db.execute(text("DELETE FROM applications WHERE user_id = :user_id"), {"user_id": str(user.id)}).rowcount

        db.commit()

        return {
            "success": True,
            "message": f"Deleted {deleted_count} applications and all documents",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Delete failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.patch("/{application_id}/rename")
async def rename_application(
    application_id: int,
    request: RenameApplicationRequest,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Rename application (folder)"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    old_name = app.company_name
    app.company_name = request.new_name
    app.updated_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "message": f"Renamed from '{old_name}' to '{request.new_name}'",
        "application_id": application_id,
        "new_name": request.new_name
    }


@router.delete("/{application_id}")
async def delete_application(
    application_id: int,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Delete application and all associated documents (CASCADE)"""
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    company_name = app.company_name

    # Delete from Elasticsearch first
    try:
        deleted_count = application_es_service.delete_by_application(application_id)
        logger.info(f"Deleted {deleted_count} documents from Elasticsearch for application {application_id}")
    except Exception as e:
        logger.error(f"Failed to delete from Elasticsearch: {e}")
        # Continue anyway - database is source of truth

    # Delete from database (CASCADE will delete documents)
    db.delete(app)
    db.commit()

    return {
        "success": True,
        "message": f"Application for {company_name} deleted successfully"
    }


@router.get("/{application_id}/documents/{document_id}/content")
async def get_document_content(
    application_id: int,
    document_id: int,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Get extracted text content of a document"""
    # Verify application ownership
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Find document
    document = db.query(ApplicationDocument).filter(
        ApplicationDocument.id == document_id,
        ApplicationDocument.application_id == application_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "filename": document.filename,
        "doc_type": document.doc_type,
        "content": document.content,
        "created_at": document.created_at
    }


@router.post("/{application_id}/documents/{document_id}/move")
async def move_document(
    application_id: int,
    document_id: int,
    request: MoveDocumentRequest,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Move document to another application (folder)"""
    # Verify source application ownership
    source_app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not source_app:
        raise HTTPException(status_code=404, detail="Source application not found")

    # Verify target application ownership
    target_app = db.query(Application).filter(
        Application.id == request.target_application_id,
        Application.user_id == user.id
    ).first()

    if not target_app:
        raise HTTPException(status_code=404, detail="Target application not found")

    # Find document
    document = db.query(ApplicationDocument).filter(
        ApplicationDocument.id == document_id,
        ApplicationDocument.application_id == application_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Move document
    old_app_name = source_app.company_name
    document.application_id = request.target_application_id

    # Update Elasticsearch if indexed
    if document.indexed:
        try:
            application_es_service.delete_document(document_id)
            application_es_service.index_document(
                document_id=document.id,
                application_id=request.target_application_id,
                user_id=str(user.id),
                company_name=target_app.company_name,
                position=target_app.position,
                filename=document.filename,
                file_path=document.file_path or document.filename,
                doc_type=document.doc_type,
                content=document.content or "",
                created_at=document.created_at.isoformat() if document.created_at else datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.error(f"Failed to update Elasticsearch: {e}")

    db.commit()

    return {
        "success": True,
        "message": f"Moved {document.filename} from '{old_app_name}' to '{target_app.company_name}'"
    }


@router.delete("/{application_id}/documents/{document_id}")
async def delete_document(
    application_id: int,
    document_id: int,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Delete a single document from an application"""
    # Verify application ownership
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Find document
    document = db.query(ApplicationDocument).filter(
        ApplicationDocument.id == document_id,
        ApplicationDocument.application_id == application_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    filename = document.filename

    # Delete from Elasticsearch
    try:
        application_es_service.delete_document(document_id)
        logger.info(f"Deleted document {document_id} from Elasticsearch")
    except Exception as e:
        logger.error(f"Failed to delete from Elasticsearch: {e}")
        # Continue anyway

    # Delete from database
    db.delete(document)
    db.commit()

    return {
        "success": True,
        "message": f"Document {filename} deleted successfully"
    }


@router.post("/upload/directory")
async def upload_application_directory(
    files: List[UploadFile] = File(...),
    company_name: str = Form(None),  # Optional - will be extracted if not provided
    position: str = Form(None),  # Optional - will be extracted if not provided
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Upload multiple application documents (supports directory upload and multiple files)

    Company name and position can be:
    - Provided manually (override)
    - Auto-extracted from documents using LLM
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    parser = DocumentParser()

    # Phase 1: Parse all documents first (to extract company/position if needed)
    parsed_files = []
    all_text = []

    for uploaded_file in files:
        try:
            file_data = await uploaded_file.read()
            filename = uploaded_file.filename

            if not filename or filename.endswith('/') or len(file_data) == 0:
                continue

            display_filename = filename.split('/')[-1] if '/' in filename else filename
            extracted_text = await parser.parse_file(display_filename, file_data)

            parsed_files.append({
                "filename": filename,
                "display_filename": display_filename,
                "data": file_data,
                "text": extracted_text
            })

            # Collect text for LLM extraction
            if extracted_text:
                all_text.append(extracted_text[:1000])  # First 1000 chars of each doc

        except Exception as e:
            logger.error(f"Failed to parse {uploaded_file.filename}: {e}")
            continue

    # Phase 2: Extract company/position if not provided manually
    if not company_name or not position:
        combined_text = "\n\n".join(all_text[:3])  # Use first 3 documents
        extracted_info = extract_application_info(combined_text)

        # Use extracted values if manual values not provided
        final_company = company_name if company_name else extracted_info.get("company_name")
        final_position = position if position else extracted_info.get("position")

        logger.info(f"Extracted: Company={final_company}, Position={final_position}")
    else:
        final_company = company_name
        final_position = position

    if not final_company:
        raise HTTPException(
            status_code=400,
            detail="Could not extract company name. Please provide it manually."
        )

    # Phase 3: Create application entry
    application = Application(
        user_id=user.id,
        company_name=final_company,
        position=final_position,
        status="uploaded",
        upload_path=f"{len(files)} files uploaded"
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    vector_service = VectorService()

    processed_files = []
    errors = []

    try:
        # Phase 4: Process already-parsed files
        for parsed_file in parsed_files:
            try:
                filename = parsed_file["filename"]
                display_filename = parsed_file["display_filename"]
                extracted_text = parsed_file["text"]

                # Determine document type
                doc_type = guess_doc_type(filename)

                # Generate embedding
                embedding = vector_service.generate_embedding(extracted_text)

                # Save document
                document = ApplicationDocument(
                    application_id=application.id,
                    filename=display_filename,
                    file_path=filename,  # Keep full path for reference
                    doc_type=doc_type,
                    content=extracted_text,
                    embedding=embedding
                )
                db.add(document)
                db.flush()  # Get document ID before Elasticsearch indexing

                # Index in Elasticsearch for hybrid search
                try:
                    application_es_service.index_document(
                        document_id=document.id,
                        application_id=application.id,
                        user_id=str(user.id),
                        company_name=final_company,
                        position=final_position,
                        filename=display_filename,
                        file_path=filename,
                        doc_type=doc_type,
                        content=extracted_text or "",
                        created_at=document.created_at.isoformat() if document.created_at else datetime.utcnow().isoformat()
                    )
                except Exception as es_error:
                    logger.error(f"Elasticsearch indexing failed for {display_filename}: {es_error}")
                    # Continue anyway - Elasticsearch is optional enhancement

                processed_files.append({
                    "filename": display_filename,
                    "type": doc_type,
                    "chars": len(extracted_text) if extracted_text else 0
                })

            except Exception as e:
                errors.append({"filename": filename, "error": str(e)})

        db.commit()

    except Exception as e:
        db.rollback()
        db.delete(application)
        db.commit()
        raise HTTPException(status_code=400, detail=f"File processing failed: {str(e)}")

    return {
        "success": True,
        "application_id": application.id,
        "company_name": final_company,
        "position": final_position,
        "processed_files": processed_files,
        "total_files": len(processed_files),
        "errors": errors,
        "extracted": not (company_name and position)  # True if auto-extracted
    }


@router.post("/upload/batch")
async def upload_batch_applications(
    files: List[UploadFile] = File(...),
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Batch upload: Upload entire directory structure with multiple applications

    Directory structure example:
    Bewerbungen/
      ├── Allianz/
      │   ├── CV.pdf
      │   └── Anschreiben.docx
      ├── SAP/
      │   ├── CV.pdf
      │   └── Anschreiben.docx

    Each first-level subdirectory becomes a separate application.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    # Group files by company (first-level directory)
    companies = {}
    for uploaded_file in files:
        filename = uploaded_file.filename

        # Skip empty files or directory markers
        if not filename or filename.endswith('/'):
            continue

        # Extract company name from path (first directory level)
        parts = filename.split('/')
        if len(parts) < 2:
            # File in root - skip or use filename as company
            continue

        company_name = parts[0]  # First directory = company name

        if company_name not in companies:
            companies[company_name] = []

        companies[company_name].append(uploaded_file)

    if not companies:
        raise HTTPException(status_code=400, detail="No valid company directories found")

    parser = DocumentParser()
    vector_service = VectorService()

    results = []
    total_applications = 0
    total_files_processed = 0
    total_errors = []

    # Process each company separately
    for company_name, company_files in companies.items():
        try:
            # Phase 1: Parse all files for this company
            parsed_files = []
            all_text = []

            for uploaded_file in company_files:
                try:
                    await uploaded_file.seek(0)
                    file_data = await uploaded_file.read()
                    filename = uploaded_file.filename

                    if len(file_data) == 0:
                        continue

                    display_filename = filename.split('/')[-1] if '/' in filename else filename
                    extracted_text = await parser.parse_file(display_filename, file_data)

                    parsed_files.append({
                        "filename": filename,
                        "display_filename": display_filename,
                        "data": file_data,
                        "text": extracted_text
                    })

                    if extracted_text:
                        all_text.append(extracted_text[:1000])

                except Exception as e:
                    logger.error(f"Failed to parse {uploaded_file.filename}: {e}")
                    continue

            # Phase 2: Extract position from documents
            position = None
            if all_text:
                combined_text = "\n\n".join(all_text[:3])
                extracted_info = extract_application_info(combined_text)
                position = extracted_info.get("position")
                logger.info(f"Extracted position for {company_name}: {position}")

            # Phase 3: Create application entry
            application = Application(
                user_id=user.id,
                company_name=company_name,
                position=position,
                status="uploaded",
                upload_path=f"{len(company_files)} files from batch upload"
            )
            db.add(application)
            db.commit()
            db.refresh(application)

            processed_files = []
            errors = []

            # Phase 4: Process already-parsed files
            for parsed_file in parsed_files:
                try:
                    filename = parsed_file["filename"]
                    display_filename = parsed_file["display_filename"]
                    extracted_text = parsed_file["text"]

                    # Determine document type using LLM classification
                    doc_type = classify_document_with_llm(extracted_text, display_filename)
                    logger.info(f"Classified {display_filename} as: {doc_type}")
                    embedding = vector_service.generate_embedding(extracted_text)

                    # Save document
                    document = ApplicationDocument(
                        application_id=application.id,
                        filename=display_filename,
                        file_path=filename,
                        doc_type=doc_type,
                        content=extracted_text,
                        embedding=embedding
                    )
                    db.add(document)
                    db.flush()  # Get document ID

                    # Index in Elasticsearch
                    try:
                        application_es_service.index_document(
                            document_id=document.id,
                            application_id=application.id,
                            user_id=str(user.id),
                            company_name=company_name,
                            position=position,  # Extracted position
                            filename=display_filename,
                            file_path=filename,
                            doc_type=doc_type,
                            content=extracted_text or "",
                            created_at=document.created_at.isoformat() if document.created_at else datetime.utcnow().isoformat()
                        )
                    except Exception as es_error:
                        logger.error(f"Elasticsearch indexing failed: {es_error}")

                    processed_files.append({
                        "filename": display_filename,
                        "type": doc_type,
                        "chars": len(extracted_text) if extracted_text else 0
                    })

                except Exception as e:
                    errors.append({"filename": filename, "error": str(e)})

            db.commit()

            results.append({
                "company_name": company_name,
                "position": position,  # Include extracted position
                "application_id": application.id,
                "processed_files": processed_files,
                "total_files": len(processed_files),
                "errors": errors
            })

            total_applications += 1
            total_files_processed += len(processed_files)
            total_errors.extend(errors)

        except Exception as e:
            total_errors.append({"company": company_name, "error": str(e)})
            db.rollback()
            continue

    return {
        "success": True,
        "total_applications": total_applications,
        "total_files": total_files_processed,
        "applications": results,
        "errors": total_errors
    }


@router.post("/files/upload")
async def upload_files_only(
    files: List[UploadFile] = File(...),
    application_id: Optional[int] = Form(None),
    company_name: Optional[str] = Form(None),
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Upload files with folder structure preservation (up to 10 levels)"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    parser = DocumentParser()

    if application_id:
        app = db.query(Application).filter(
            Application.id == application_id,
            Application.user_id == user.id
        ).first()
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
    else:
        final_company = company_name or "Neue Bewerbung"
        app = Application(
            user_id=user.id,
            company_name=final_company,
            position=None,
            status="uploaded",
            upload_path=f"{len(files)} files uploaded"
        )
        db.add(app)
        db.commit()
        db.refresh(app)

    uploaded_files = []
    errors = []

    # Cache for created folders: {path: folder_id}
    folder_cache = {}

    def get_or_create_folder(folder_path_parts, current_index=0, parent_id=None):
        """Recursively create folder hierarchy"""
        if current_index >= len(folder_path_parts):
            return parent_id

        folder_name = folder_path_parts[current_index]

        # Build path up to current level
        if parent_id:
            parent = db.query(ApplicationFolder).filter(
                ApplicationFolder.id == parent_id
            ).first()
            full_path = f"{parent.path}/{folder_name}"
        else:
            full_path = f"/{folder_name}"

        # Check cache first
        if full_path in folder_cache:
            return get_or_create_folder(folder_path_parts, current_index + 1, folder_cache[full_path])

        # Check if folder exists
        existing = db.query(ApplicationFolder).filter(
            ApplicationFolder.application_id == app.id,
            ApplicationFolder.path == full_path
        ).first()

        if existing:
            folder_cache[full_path] = existing.id
            return get_or_create_folder(folder_path_parts, current_index + 1, existing.id)

        # Create new folder
        level = current_index
        if level >= 10:
            raise HTTPException(status_code=400, detail=f"Maximum folder depth (10 levels) exceeded in path: {full_path}")

        new_folder = ApplicationFolder(
            application_id=app.id,
            name=folder_name,
            parent_id=parent_id,
            path=full_path,
            level=level
        )
        db.add(new_folder)
        db.flush()

        folder_cache[full_path] = new_folder.id

        # Continue with next level
        return get_or_create_folder(folder_path_parts, current_index + 1, new_folder.id)

    for uploaded_file in files:
        try:
            file_data = await uploaded_file.read()
            filename = uploaded_file.filename

            if not filename or filename.endswith('/') or len(file_data) == 0:
                continue

            # Parse folder structure from filename
            # Format: "Bewerbungen/Januar/Firma A/cv.pdf" or just "cv.pdf"
            path_parts = filename.split('/')

            if len(path_parts) > 1:
                # Has folder structure
                folder_parts = path_parts[:-1]  # All except filename
                display_filename = path_parts[-1]  # Just the filename

                # Create folder hierarchy and get the folder_id
                folder_id = get_or_create_folder(folder_parts)
            else:
                # No folder structure - just a file
                display_filename = filename
                folder_id = None

            # Extract text from file
            extracted_text = await parser.parse_file(display_filename, file_data)

            # Create document with folder_id
            document = ApplicationDocument(
                application_id=app.id,
                folder_id=folder_id,
                filename=display_filename,
                file_path=filename,
                content=extracted_text,
                doc_type=None,
                embedding=None,
                indexed=False
            )
            db.add(document)
            db.flush()

            uploaded_files.append({
                "id": document.id,
                "filename": display_filename,
                "folder_path": '/'.join(folder_parts) if len(path_parts) > 1 else None,
                "indexed": False
            })

        except Exception as e:
            logger.error(f"Failed to upload {uploaded_file.filename}: {e}")
            errors.append({"filename": uploaded_file.filename, "error": str(e)})

    db.commit()

    return {
        "success": True,
        "application_id": app.id,
        "company_name": app.company_name,
        "uploaded_files": uploaded_files,
        "total_files": len(uploaded_files),
        "errors": errors,
        "folders_created": len(folder_cache)
    }


@router.post("/documents/{document_id}/index")
async def index_document_manually(
    document_id: int,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Manually index a document: LLM + embeddings + Elasticsearch"""
    document = db.query(ApplicationDocument).join(Application).filter(
        ApplicationDocument.id == document_id,
        Application.user_id == user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.indexed:
        return {
            "success": True,
            "message": "Document already indexed",
            "document_id": document_id
        }

    try:
        doc_type = classify_document_with_llm(
            document.content[:1500] if document.content else "",
            document.filename
        )
        logger.info(f"Classified {document.filename} as: {doc_type}")

        vector_service = VectorService()
        embedding = vector_service.generate_embedding(document.content or "")

        try:
            application_es_service.index_document(
                document_id=document.id,
                application_id=document.application_id,
                user_id=str(user.id),
                company_name=document.application.company_name,
                position=document.application.position,
                filename=document.filename,
                file_path=document.file_path or document.filename,
                doc_type=doc_type,
                content=document.content or "",
                created_at=document.created_at.isoformat() if document.created_at else datetime.utcnow().isoformat()
            )
        except Exception as es_error:
            logger.error(f"Elasticsearch indexing failed: {es_error}")

        document.doc_type = doc_type
        document.embedding = embedding
        document.indexed = True

        db.commit()

        return {
            "success": True,
            "message": "Document indexed successfully",
            "document_id": document_id,
            "doc_type": doc_type
        }

    except Exception as e:
        logger.error(f"Failed to index document {document_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.get("/files/list")
async def list_all_files(
    application_id: Optional[int] = None,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """List all applications (folders) and their files

    Ein Folder = eine Bewerbung (Application)
    """
    # Get all applications for this user
    applications = db.query(Application).filter(Application.user_id == user.id).all()

    folders = []
    for app in applications:
        # Get document count and indexed count
        doc_count = db.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == app.id
        ).count()

        indexed_count = db.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == app.id,
            ApplicationDocument.indexed == True
        ).count()

        folders.append({
            "id": app.id,
            "type": "folder",
            "company_name": app.company_name,
            "position": app.position,
            "status": app.status,
            "document_count": doc_count,
            "indexed_count": indexed_count,
            "created_at": app.created_at.isoformat() if app.created_at else None
        })

    # If specific application_id requested, also return its files
    files = []
    if application_id:
        documents = db.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == application_id
        ).order_by(ApplicationDocument.created_at.desc()).all()

        for doc in documents:
            files.append({
                "id": doc.id,
                "type": "file",
                "application_id": doc.application_id,
                "filename": doc.filename,
                "doc_type": doc.doc_type,
                "indexed": doc.indexed,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            })

    return {
        "success": True,
        "folders": folders,
        "files": files,
        "total_folders": len(folders),
        "total_files": len(files)
    }


# ========================================
# HIERARCHICAL FOLDER ENDPOINTS (Up to 10 levels)
# ========================================

@router.get("/folders", response_model=List[FolderResponse])
async def list_folders(
    application_id: int,
    parent_id: Optional[int] = None,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """List folders for an application

    If parent_id is None, returns root level folders
    Otherwise returns children of the specified folder
    """
    # Verify application belongs to user
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Query folders
    query = db.query(ApplicationFolder).filter(
        ApplicationFolder.application_id == application_id
    )

    if parent_id is None:
        query = query.filter(ApplicationFolder.parent_id.is_(None))
    else:
        query = query.filter(ApplicationFolder.parent_id == parent_id)

    folders = query.order_by(ApplicationFolder.name).all()

    return folders


@router.post("/folders", response_model=FolderResponse)
async def create_folder(
    application_id: int,
    request: CreateFolderRequest,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Create a new folder (up to 10 levels deep)"""
    # Verify application belongs to user
    app = db.query(Application).filter(
        Application.id == application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Calculate level and path
    level = 0
    path = f"/{request.name}"

    if request.parent_id:
        parent = db.query(ApplicationFolder).filter(
            ApplicationFolder.id == request.parent_id,
            ApplicationFolder.application_id == application_id
        ).first()

        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")

        level = parent.level + 1

        if level >= 10:
            raise HTTPException(status_code=400, detail="Maximum folder depth (10 levels) reached")

        path = f"{parent.path}/{request.name}"

    # Create folder
    folder = ApplicationFolder(
        application_id=application_id,
        name=request.name,
        parent_id=request.parent_id,
        path=path,
        level=level
    )

    db.add(folder)
    db.commit()
    db.refresh(folder)

    return folder


@router.patch("/folders/{folder_id}/rename", response_model=FolderResponse)
async def rename_folder(
    folder_id: int,
    request: RenameFolderRequest,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Rename folder and update all child paths recursively"""
    # Get folder and verify ownership
    folder = db.query(ApplicationFolder).filter(
        ApplicationFolder.id == folder_id
    ).first()

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Verify user owns the application
    app = db.query(Application).filter(
        Application.id == folder.application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=403, detail="Access denied")

    # Store old path for recursive update
    old_path = folder.path

    # Calculate new path
    if folder.parent_id:
        parent = db.query(ApplicationFolder).filter(
            ApplicationFolder.id == folder.parent_id
        ).first()
        new_path = f"{parent.path}/{request.new_name}"
    else:
        new_path = f"/{request.new_name}"

    # Update folder
    folder.name = request.new_name
    folder.path = new_path

    # Recursively update all children paths
    def update_children_paths(parent_folder):
        children = db.query(ApplicationFolder).filter(
            ApplicationFolder.parent_id == parent_folder.id
        ).all()

        for child in children:
            # Replace old parent path with new parent path
            child.path = child.path.replace(old_path, new_path, 1)
            update_children_paths(child)

    update_children_paths(folder)

    db.commit()
    db.refresh(folder)

    return folder


@router.post("/folders/{folder_id}/move", response_model=FolderResponse)
async def move_folder(
    folder_id: int,
    request: MoveFolderRequest,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Move folder to new parent (updates all child paths recursively)"""
    # Get folder
    folder = db.query(ApplicationFolder).filter(
        ApplicationFolder.id == folder_id
    ).first()

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Verify user owns the application
    app = db.query(Application).filter(
        Application.id == folder.application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=403, detail="Access denied")

    # Prevent moving folder into itself or its children
    if request.target_parent_id == folder_id:
        raise HTTPException(status_code=400, detail="Cannot move folder into itself")

    if request.target_parent_id:
        # Check if target is a descendant
        target = db.query(ApplicationFolder).filter(
            ApplicationFolder.id == request.target_parent_id
        ).first()

        if not target or target.application_id != folder.application_id:
            raise HTTPException(status_code=404, detail="Target folder not found")

        # Check depth limit
        new_level = target.level + 1

        # Calculate max depth of subtree being moved
        def get_max_depth(f, current_depth=0):
            children = db.query(ApplicationFolder).filter(
                ApplicationFolder.parent_id == f.id
            ).all()

            if not children:
                return current_depth

            return max(get_max_depth(child, current_depth + 1) for child in children)

        subtree_depth = get_max_depth(folder)

        if new_level + subtree_depth >= 10:
            raise HTTPException(status_code=400, detail="Moving would exceed maximum depth (10 levels)")

        # Prevent circular reference
        current = target
        while current:
            if current.id == folder_id:
                raise HTTPException(status_code=400, detail="Cannot move folder into its own descendant")
            current = db.query(ApplicationFolder).filter(
                ApplicationFolder.id == current.parent_id
            ).first() if current.parent_id else None

    old_path = folder.path

    # Update folder
    if request.target_parent_id:
        target = db.query(ApplicationFolder).filter(
            ApplicationFolder.id == request.target_parent_id
        ).first()
        folder.parent_id = request.target_parent_id
        folder.level = target.level + 1
        folder.path = f"{target.path}/{folder.name}"
    else:
        # Move to root
        folder.parent_id = None
        folder.level = 0
        folder.path = f"/{folder.name}"

    new_path = folder.path

    # Recursively update all children
    def update_children(parent_folder, level_diff):
        children = db.query(ApplicationFolder).filter(
            ApplicationFolder.parent_id == parent_folder.id
        ).all()

        for child in children:
            child.path = child.path.replace(old_path, new_path, 1)
            child.level += level_diff
            update_children(child, level_diff)

    level_diff = folder.level - (target.level + 1 if request.target_parent_id else 0)
    update_children(folder, level_diff)

    db.commit()
    db.refresh(folder)

    return folder


@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: int,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Delete folder recursively (all children and documents)"""
    # Get folder
    folder = db.query(ApplicationFolder).filter(
        ApplicationFolder.id == folder_id
    ).first()

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Verify user owns the application
    app = db.query(Application).filter(
        Application.id == folder.application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=403, detail="Access denied")

    # Recursively delete all children and documents
    def delete_recursive(f):
        # Get all children
        children = db.query(ApplicationFolder).filter(
            ApplicationFolder.parent_id == f.id
        ).all()

        # Delete children first
        for child in children:
            delete_recursive(child)

        # Delete all documents in this folder
        db.query(ApplicationDocument).filter(
            ApplicationDocument.folder_id == f.id
        ).delete()

        # Delete the folder
        db.delete(f)

    delete_recursive(folder)
    db.commit()

    return {"success": True, "message": "Folder deleted recursively"}


@router.post("/folders/{folder_id}/index-all")
async def index_folder_recursively(
    folder_id: int,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Index all documents in folder and subfolders recursively"""
    # Get folder
    folder = db.query(ApplicationFolder).filter(
        ApplicationFolder.id == folder_id
    ).first()

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Verify user owns the application
    app = db.query(Application).filter(
        Application.id == folder.application_id,
        Application.user_id == user.id
    ).first()

    if not app:
        raise HTTPException(status_code=403, detail="Access denied")

    # Collect all folder IDs recursively
    folder_ids = []

    def collect_folder_ids(f):
        folder_ids.append(f.id)
        children = db.query(ApplicationFolder).filter(
            ApplicationFolder.parent_id == f.id
        ).all()
        for child in children:
            collect_folder_ids(child)

    collect_folder_ids(folder)

    # Get all documents in these folders
    documents = db.query(ApplicationDocument).filter(
        ApplicationDocument.folder_id.in_(folder_ids)
    ).all()

    # Index each document
    vector_service = VectorService()
    indexed_count = 0
    failed_count = 0

    for doc in documents:
        try:
            if doc.content:
                # Generate embedding
                embedding = await vector_service.generate_embedding(doc.content)
                doc.embedding = embedding

                # Index in Elasticsearch
                application_es_service.index_document(
                    document_id=doc.id,
                    filename=doc.filename,
                    content=doc.content,
                    company_name=app.company_name,
                    position=app.position or "",
                    user_id=str(user.id)
                )

                doc.indexed = True
                indexed_count += 1
        except Exception as e:
            logger.error(f"Failed to index document {doc.id}: {e}")
            failed_count += 1

    db.commit()

    return {
        "success": True,
        "total_documents": len(documents),
        "indexed": indexed_count,
        "failed": failed_count,
        "folders_processed": len(folder_ids)
    }


@router.post("/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Send chat message and get response with RAG"""
    user_message = ApplicationChatMessage(
        user_id=user.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    db.commit()

    action_taken = await _check_status_update(request.message, user.id, db)

    # HYBRID SEARCH: Combine Elasticsearch (keyword) + pgvector (semantic)

    # 1. Elasticsearch: Full-text search with fuzzy matching
    es_results = application_es_service.search(
        query=request.message,
        user_id=str(user.id),
        limit=10
    )
    es_doc_ids = {r["document_id"]: r["score"] for r in es_results}

    # 2. pgvector: Semantic similarity search
    vector_service = VectorService()
    query_embedding = await vector_service.generate_embedding(request.message)

    documents = db.query(ApplicationDocument).join(Application).filter(
        Application.user_id == user.id
    ).all()

    vector_results = {}
    for doc in documents:
        if doc.embedding:
            similarity = vector_service.cosine_similarity(query_embedding, doc.embedding)
            if similarity > 0.3:
                vector_results[doc.id] = {
                    "id": doc.id,
                    "filename": doc.filename,
                    "similarity": similarity,
                    "content": doc.content[:500] if doc.content else "",
                    "company": doc.application.company_name if doc.application else ""
                }

    # 3. Combine results (Hybrid Ranking)
    # Documents found by both get higher score
    all_doc_ids = set(es_doc_ids.keys()) | set(vector_results.keys())
    relevant_docs = []

    for doc_id in all_doc_ids:
        es_score = es_doc_ids.get(doc_id, 0) / 10.0  # Normalize ES score
        vector_score = vector_results.get(doc_id, {}).get("similarity", 0)

        # Hybrid score: Weighted combination
        hybrid_score = (0.6 * vector_score) + (0.4 * es_score)

        if doc_id in vector_results:
            doc_info = vector_results[doc_id]
            doc_info["hybrid_score"] = hybrid_score
            doc_info["es_score"] = es_score
            relevant_docs.append(doc_info)

    relevant_docs.sort(key=lambda x: x.get("hybrid_score", 0), reverse=True)
    relevant_docs = relevant_docs[:5]

    applications = db.query(Application).filter(Application.user_id == user.id).all()
    app_summary = "\n".join([
        f"- {app.company_name} ({app.position or 'N/A'}): {app.status}"
        for app in applications
    ])

    context_parts = []
    if app_summary:
        context_parts.append(f"=== Bewerbungen ===\n{app_summary}")
    if relevant_docs:
        docs_text = "\n\n".join([
            f"Dokument: {doc['filename']} (Relevanz: {doc['similarity']:.2f})\n{doc['content']}"
            for doc in relevant_docs
        ])
        context_parts.append(f"=== Relevante Dokumente ===\n{docs_text}")

    context = "\n\n".join(context_parts)

    system_prompt = """Du bist ein intelligenter Assistent für Bewerbungsmanagement.
Beantworte Fragen zu Bewerbungen und Dokumenten präzise auf Deutsch."""

    full_prompt = f"Kontext:\n{context}\n\nFrage: {request.message}\n\nAntwort:"

    response_text = await llm_gateway.generate(
        message=full_prompt,
        system_prompt=system_prompt,
        llm_type=request.provider,
        temperature=0.7,
        max_tokens=1500
    )

    assistant_message = ApplicationChatMessage(
        user_id=user.id,
        role="assistant",
        content=response_text
    )
    db.add(assistant_message)
    db.commit()

    return ChatMessageResponse(
        message=response_text,
        context_used=relevant_docs,
        action_taken=action_taken
    )


async def _check_status_update(message: str, user_id, db: Session):
    """Check if message contains status update intent"""
    message_lower = message.lower()

    status_map = {
        'uploaded': ['hochgeladen', 'uploaded'],
        'applied': ['beworben', 'applied'],
        'interview': ['interview', 'gespräch'],
        'offer': ['zusage', 'offer'],
        'rejected': ['absage', 'rejected'],
        'accepted': ['angenommen', 'accepted']
    }

    patterns = [
        r'(?:status\s+)?([a-z0-9äöüß\s]+?)\s+(?:auf|to)\s+([a-z\s]+)',
        r'update\s+([a-z0-9äöüß\s]+?)\s+(?:auf|to)\s+([a-z\s]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            company_partial = match.group(1).strip()
            status_keyword = match.group(2).strip()

            new_status = None
            for status, keywords in status_map.items():
                if any(kw in status_keyword for kw in keywords):
                    new_status = status
                    break

            if new_status:
                apps = db.query(Application).filter(Application.user_id == user_id).all()
                for app in apps:
                    if company_partial in app.company_name.lower():
                        old_status = app.status
                        app.status = new_status
                        history = ApplicationStatusHistory(
                            application_id=app.id,
                            old_status=old_status,
                            new_status=new_status,
                            notes=f"Via chat: {message}"
                        )
                        db.add(history)
                        db.commit()
                        return {
                            "action": "status_update",
                            "company": app.company_name,
                            "old_status": old_status,
                            "new_status": new_status
                        }
    return None


@router.get("/reports/status")
async def get_status_report(
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Get status report"""
    status_counts = db.query(
        Application.status,
        func.count(Application.id).label('count')
    ).filter(Application.user_id == user.id).group_by(Application.status).all()

    total = db.query(func.count(Application.id)).filter(
        Application.user_id == user.id
    ).scalar()

    recent = db.query(ApplicationStatusHistory).join(Application).filter(
        Application.user_id == user.id
    ).order_by(desc(ApplicationStatusHistory.changed_at)).limit(10).all()

    return {
        "total_applications": total,
        "status_distribution": [{"status": s, "count": c} for s, c in status_counts],
        "recent_changes": [{
            "application_id": r.application_id,
            "old_status": r.old_status,
            "new_status": r.new_status,
            "changed_at": r.changed_at
        } for r in recent]
    }


@router.post("/reports/generate", response_model=ReportResponse)
async def generate_report(
    request: GenerateReportRequest,
    user: User = Depends(get_demo_user),
    db: Session = Depends(get_db)
):
    """Generate custom report"""
    apps = db.query(Application).filter(Application.user_id == user.id).all()

    columns = request.columns + [c.name for c in request.custom_columns]
    rows = []

    for app in apps:
        row = {}
        doc_count = db.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == app.id
        ).count()

        for col in request.columns:
            if col == "company_name": row[col] = app.company_name
            elif col == "position": row[col] = app.position or "N/A"
            elif col == "status": row[col] = app.status
            elif col == "document_count": row[col] = doc_count
            elif col == "created_at": row[col] = app.created_at.isoformat()

        for custom_col in request.custom_columns:
            if custom_col.prompt:
                docs = db.query(ApplicationDocument).filter(
                    ApplicationDocument.application_id == app.id
                ).limit(2).all()
                doc_text = "\n".join([d.content[:300] for d in docs if d.content])

                prompt = f"Firma: {app.company_name}\nPosition: {app.position}\nDokumente: {doc_text}\n\n{custom_col.prompt}"

                value = await llm_gateway.generate(
                    message=prompt,
                    llm_type=request.provider,
                    max_tokens=150
                )

                if custom_col.type == "number":
                    nums = re.findall(r'\d+', value)
                    row[custom_col.name] = int(nums[0]) if nums else 0
                else:
                    row[custom_col.name] = value.strip()
            else:
                row[custom_col.name] = ""

        rows.append(row)

    return ReportResponse(
        columns=columns,
        rows=rows,
        total_rows=len(rows),
        generated_at=datetime.utcnow()
    )
